import streamlit as st
import vosk
import sounddevice as sd
import queue
import json
import threading
import sys
import time
import os
import wave
import numpy as np
from io import BytesIO
import scipy.signal

# --- Application State Management ---
# Use Streamlit's session state to manage our app's state across reruns.
if 'vosk_worker_thread' not in st.session_state:
    st.session_state.vosk_worker_thread = None
if 'text_queue' not in st.session_state:
    st.session_state.text_queue = queue.Queue()
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'full_text' not in st.session_state:
    st.session_state.full_text = ""
if 'partial_text' not in st.session_state:
    st.session_state.partial_text = ""
if 'stop_event' not in st.session_state:
    st.session_state.stop_event = threading.Event()
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = {}
if 'audio_initialized' not in st.session_state:
    st.session_state.audio_initialized = False
if 'uploaded_file_text' not in st.session_state:
    st.session_state.uploaded_file_text = ""
if 'processing_file' not in st.session_state:
    st.session_state.processing_file = False

# --- MODEL LOADING ---
@st.cache_resource
def load_vosk_model(model_path):
    """Load and cache Vosk model"""
    try:
        if not os.path.exists(model_path):
            return None, f"Model directory not found: {model_path}"
        
        model = vosk.Model(model_path)
        return model, "Model loaded successfully"
    except Exception as e:
        return None, f"Error loading model: {str(e)}"

# --- AUDIO DEVICE CHECK ---
def check_audio_devices():
    """Check if audio input devices are available"""
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        return len(input_devices) > 0, input_devices
    except Exception as e:
        return False, str(e)

# --- AUDIO FILE PROCESSING ---
def process_audio_file(model, audio_file, language):
    """Process uploaded audio file and return transcription"""
    try:
        if model is None:
            return None, f"Model for {language} is not available"
        
        # Read the uploaded file
        audio_bytes = audio_file.read()
        
        if len(audio_bytes) == 0:
            return None, "Audio file is empty"
        
        # Create a BytesIO object from the audio bytes
        audio_io = BytesIO(audio_bytes)
        
        # Open the audio file with wave
        with wave.open(audio_io, 'rb') as wf:
            # Get file properties
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            sample_rate = wf.getframerate()
            frames = wf.getnframes()
            
            # Provide detailed file info for debugging
            print(f"Audio file info: {channels} channels, {sampwidth*8}-bit, {sample_rate}Hz, {frames} frames")
            
            # Check file format requirements
            if channels != 1:
                return None, f"Audio file must be mono (single channel), found {channels} channels"
            
            if sampwidth != 2:
                return None, f"Audio file must be 16-bit, found {sampwidth*8}-bit"
            
            if frames == 0:
                return None, "Audio file contains no audio frames"
            
            # Read all audio data
            audio_data = wf.readframes(frames)
            
            # Convert to numpy array for processing
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Handle sample rate conversion if needed
            if sample_rate != 16000:
                print(f"Converting sample rate from {sample_rate}Hz to 16000Hz")
                # Calculate the number of samples for 16kHz
                target_samples = int(len(audio_array) * 16000 / sample_rate)
                # Resample the audio
                audio_array = scipy.signal.resample(audio_array, target_samples).astype(np.int16)
                sample_rate = 16000
            
        # Initialize recognizer with 16kHz sample rate
        recognizer = vosk.KaldiRecognizer(model, 16000)
        recognizer.SetWords(True)
        
        transcription_parts = []
        
        # Process audio in chunks
        chunk_size = 4000  # Process 4000 samples at a time
        total_samples = len(audio_array)
        
        print(f"Processing {total_samples} samples in chunks of {chunk_size}")
        
        for i in range(0, total_samples, chunk_size):
            # Get chunk of audio data
            chunk = audio_array[i:i + chunk_size]
            
            # Convert chunk to bytes
            chunk_bytes = chunk.tobytes()
            
            if recognizer.AcceptWaveform(chunk_bytes):
                result = json.loads(recognizer.Result())
                if result.get('text', '').strip():
                    text = result['text'].strip()
                    transcription_parts.append(text)
                    print(f"Partial transcription: {text}")
        
        # Get final result
        final_result = json.loads(recognizer.FinalResult())
        if final_result.get('text', '').strip():
            final_text = final_result['text'].strip()
            transcription_parts.append(final_text)
            print(f"Final transcription: {final_text}")
            
            # Combine all parts
            full_transcription = ' '.join(transcription_parts)
            
            if full_transcription:
                return full_transcription, "Success"
            else:
                return None, "No speech detected in the audio file"
                
    except wave.Error as e:
        return None, f"Invalid WAV file: {str(e)}"
    except Exception as e:
        return None, f"Error processing audio file: {str(e)}"

# --- VOSK WORKER THREAD ---
def vosk_worker(model, language, text_queue_ref, stop_event):
    """
    Background thread that handles audio capture and speech recognition.
    This runs separately from the Streamlit main thread to prevent UI freezing.
    """
    try:
        # Audio configuration
        samplerate = 16000
        blocksize = 8000
        audio_queue = queue.Queue()

        def audio_callback(indata, frames, time, status):
            """Callback function to capture audio data from microphone"""
            if status:
                print(f"Audio status: {status}", file=sys.stderr)
            # Convert audio data to bytes and add to queue
            audio_queue.put(bytes(indata))

        # Initialize Vosk recognizer
        recognizer = vosk.KaldiRecognizer(model, samplerate)
        recognizer.SetWords(True)
        
        # Signal that we're starting to listen
        text_queue_ref.put({"type": "status", "text": f"🎙️ Listening with {language} model..."})
        print(f"INFO: [{language}] Vosk Worker started - listening for speech...")
        
        # Start audio input stream
        with sd.RawInputStream(
            samplerate=samplerate, 
            blocksize=blocksize,
            device=None,  # Use default input device
            dtype='int16',
            channels=1, 
            callback=audio_callback
        ):
            
            # Main recognition loop
            while not stop_event.is_set():
                try:
                    # Get audio data from queue (with timeout to check stop_event regularly)
                    data = audio_queue.get(timeout=0.1)
                    
                    # Process audio data with Vosk
                    if recognizer.AcceptWaveform(data):
                        # Final result - complete utterance recognized
                        result = json.loads(recognizer.Result())
                        if result.get('text', '').strip():
                            text_queue_ref.put({
                                "type": "final", 
                                "text": result['text'].strip()
                            })
                    else:
                        # Partial result - ongoing recognition
                        partial_result = json.loads(recognizer.PartialResult())
                        if partial_result.get('partial', '').strip():
                            text_queue_ref.put({
                                "type": "partial", 
                                "text": partial_result['partial'].strip()
                            })
                            
                except queue.Empty:
                    # No audio data available, continue loop
                    continue
                except Exception as e:
                    print(f"Error in recognition loop: {e}", file=sys.stderr)
                    break
        
        # Cleanup
        print(f"INFO: [{language}] Vosk Worker stopped gracefully.")
        text_queue_ref.put({"type": "status", "text": "⏹️ Recording stopped."})
        
    except Exception as e:
        error_message = f"ERROR: Vosk worker error for {language}: {str(e)}"
        print(error_message, file=sys.stderr)
        text_queue_ref.put({"type": "error", "text": error_message})

# --- Streamlit User Interface ---
st.set_page_config(layout="wide", page_title="WhisperBoard - Live Demo")
st.title("🎤 WhisperBoard - Live Speech Recognition")
st.markdown("**Real-time speech-to-text powered by Vosk** | Built for the Pragna Hackathon")

# Check audio system
if not st.session_state.audio_initialized:
    with st.spinner("Checking audio system..."):
        audio_ok, audio_info = check_audio_devices()
        st.session_state.audio_initialized = True
        
        if not audio_ok:
            st.error("🎤 **No microphone detected!**")
            st.error("Please ensure your microphone is connected and try refreshing the page.")
            st.stop()

# Sidebar controls
st.sidebar.header("🎛️ Controls")

# Language selection
MODELS = {
    "English (US)": "model-English",
    "Hindi (हिन्दी)": "model-Hindi",
    "Telugu (తెలుగు)": "model-Telugu"
}

language = st.sidebar.selectbox(
    "Select Language", 
    list(MODELS.keys()), 
    disabled=st.session_state.is_recording,
    help="Choose the language for speech recognition"
)

# Load model for selected language
model_path = MODELS[language]
if language not in st.session_state.model_loaded:
    with st.spinner(f"Loading {language} model..."):
        model, message = load_vosk_model(model_path)
        st.session_state.model_loaded[language] = model
        
        if model is None:
            st.sidebar.error(f"❌ {message}")
            st.error(f"**Model Loading Failed**: {message}")
            
            # Provide download instructions
            st.info("� **To download Vosk models:**")
            if language == "English (US)":
                st.code("""
# Download English model
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
mv vosk-model-en-us-0.22 model
                """)
            else:
                st.code("""
# Download Hindi model
wget https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip
unzip vosk-model-hi-0.22.zip
mv vosk-model-hi-0.22 model-hi
                """)
            st.stop()
        else:
            st.sidebar.success(f"✅ {language} model loaded")

# Recording button
model = st.session_state.model_loaded[language]
button_text = "⏹️ Stop Recording" if st.session_state.is_recording else "🔴 Start Recording"
button_disabled = model is None

if st.sidebar.button(button_text, disabled=button_disabled):
    if not st.session_state.is_recording:
        # Start recording
        st.session_state.is_recording = True
        st.session_state.stop_event.clear()
        
        # Clear previous text
        st.session_state.full_text = ""
        st.session_state.partial_text = ""
        
        # Start background worker thread
        worker_thread = threading.Thread(
            target=vosk_worker,
            args=(model, language, st.session_state.text_queue, st.session_state.stop_event),
            daemon=True  # Thread will close when main program closes
        )
        st.session_state.vosk_worker_thread = worker_thread
        worker_thread.start()
        
    else:
        # Stop recording
        st.session_state.is_recording = False
        
        # Signal worker thread to stop
        if st.session_state.vosk_worker_thread and st.session_state.vosk_worker_thread.is_alive():
            st.session_state.stop_event.set()
            st.session_state.vosk_worker_thread.join(timeout=2.0)
        
        # Clear partial text
        st.session_state.partial_text = ""
    
    # Refresh the page to update UI
    st.rerun()

# Status display
if st.session_state.is_recording:
    st.sidebar.info("🎙️ **LIVE** - Speak into your microphone")
    st.sidebar.write("The app is listening and transcribing in real-time!")
elif model:
    st.sidebar.success("✅ Ready to record")
else:
    st.sidebar.warning("⚠️ Model not loaded")

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.header("📝 Speech Recognition")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["🎙️ Live Recording", "📁 Upload Audio File"])
    
    with tab1:
        st.subheader("Real-time Microphone Input")
    
        # Combine full text and partial text for display
        display_text = st.session_state.full_text
        if st.session_state.partial_text:
            # Add partial text with visual indicator
            display_text += (" " if display_text else "") + st.session_state.partial_text + " ●"
        elif st.session_state.is_recording and language == "Telugu (తెలుగు)" and not st.session_state.full_text:
            # Special message for Telugu model (no partial results)
            display_text = "🎙️ తెలుగు లో మాట్లాడండి... (Speak in Telugu - results appear after complete phrases) ●"
        
        # Display transcription in real-time
        transcription_placeholder = st.text_area(
            "Real-time Speech Recognition",
            value=display_text,
            height=300,
            disabled=True,
            help="Live transcription will appear here as you speak"
        )
        
        # Control buttons for live recording
        col_clear, col_copy = st.columns(2)
        with col_clear:
            if st.button("🗑️ Clear Live Text", disabled=st.session_state.is_recording):
                st.session_state.full_text = ""
                st.session_state.partial_text = ""
                st.rerun()
        
        with col_copy:
            if st.session_state.full_text:
                st.download_button(
                    label="📋 Download Live Text",
                    data=st.session_state.full_text,
                    file_name=f"live_transcription_{language.lower().replace(' ', '_')}.txt",
                    mime="text/plain"
                )
    
    with tab2:
        st.subheader("Upload Audio File")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a WAV audio file",
            type=['wav'],
            help="Upload a WAV file (16kHz, 16-bit, mono) for transcription",
            disabled=st.session_state.is_recording or st.session_state.processing_file
        )
        
        if uploaded_file is not None:
            # Display file info
            st.info(f"📁 **File:** {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Show model status
            current_model = st.session_state.model_loaded.get(language)
            if current_model is not None:
                st.success(f"✅ **Model Status:** {language} model is loaded and ready")
            else:
                st.warning(f"⚠️ **Model Status:** {language} model is not loaded")
            
            # Process button
            if st.button("🔄 Process Audio File", disabled=st.session_state.is_recording or st.session_state.processing_file):
                # Get the current model for the selected language
                current_model = st.session_state.model_loaded.get(language)
                
                if current_model is None:
                    st.error(f"❌ {language} model is not loaded. Please wait for the model to load or check if the model directory exists.")
                else:
                    st.session_state.processing_file = True
                    
                    with st.spinner(f"🤖 Processing audio file with {language} model..."):
                        try:
                            # Reset the file pointer
                            uploaded_file.seek(0)
                            
                            # Process the audio file
                            transcription, message = process_audio_file(current_model, uploaded_file, language)
                            
                            if transcription:
                                st.session_state.uploaded_file_text = transcription
                                st.success("✅ Audio file processed successfully!")
                            else:
                                st.error(f"❌ {message}")
                        except Exception as e:
                            st.error(f"❌ Error processing file: {str(e)}")
                    
                    st.session_state.processing_file = False
                    st.rerun()
        
        # Display transcription from uploaded file
        if st.session_state.uploaded_file_text:
            st.text_area(
                "File Transcription Result",
                value=st.session_state.uploaded_file_text,
                height=300,
                disabled=True,
                help="Transcription from your uploaded audio file"
            )
            
            # Control buttons for file transcription
            col_clear_file, col_copy_file = st.columns(2)
            with col_clear_file:
                if st.button("🗑️ Clear File Text", disabled=st.session_state.processing_file):
                    st.session_state.uploaded_file_text = ""
                    st.rerun()
            
            with col_copy_file:
                st.download_button(
                    label="📋 Download File Text",
                    data=st.session_state.uploaded_file_text,
                    file_name=f"file_transcription_{language.lower().replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("📤 Upload a WAV audio file above to get started with file transcription.")

with col2:
    st.header("ℹ️ Status")
    
    # Current configuration
    st.subheader("Configuration")
    st.write(f"**Language:** {language}")
    st.write(f"**Model:** {model_path}")
    st.write(f"**Status:** {'🔴 Recording' if st.session_state.is_recording else '⏸️ Idle'}")
    
    # Instructions
    st.subheader("How to Use")
    
    st.write("**🎙️ Live Recording:**")
    st.write("1. Select your language")
    st.write("2. Click 'Start Recording'")
    st.write("3. Speak clearly into microphone")
    st.write("4. Watch live transcription")
    st.write("5. Click 'Stop Recording' when done")
    
    st.write("**📁 File Upload:**")
    st.write("1. Select your language")
    st.write("2. Go to 'Upload Audio File' tab")
    st.write("3. Upload a WAV file (16kHz, mono)")
    st.write("4. Click 'Process Audio File'")
    st.write("5. View transcription results")
    
    # Special note for Telugu
    if language == "Telugu (తెలుగు)":
        st.info("📝 **Telugu Note**: Text appears after complete phrases (no live preview while speaking)")
    
    # Tips
    st.subheader("💡 Tips")
    
    st.write("**🎙️ Live Recording:**")
    st.write("• Speak at normal pace")
    st.write("• Minimize background noise")
    st.write("• Use a quality microphone")
    st.write("• Stay close to the microphone")
    
    st.write("**📁 File Upload:**")
    st.write("• Use WAV format only")
    st.write("• 16kHz sample rate required")
    st.write("• 16-bit depth, mono channel")
    st.write("• Clear audio for best results")
    
    # Language-specific tips
    if language == "Telugu (తెలుగు)":
        st.write("• **Telugu**: Speak complete words/phrases")
        st.write("• **Telugu**: Pause briefly between sentences")
        st.write("• **Telugu**: Results appear after you finish speaking")
    
    # Word count
    if st.session_state.full_text:
        word_count = len(st.session_state.full_text.split())
        st.metric("Words Transcribed", word_count)

# Process messages from background thread
message_processed = False
while not st.session_state.text_queue.empty():
    try:
        result = st.session_state.text_queue.get_nowait()
        message_processed = True
        
        if result["type"] == "partial":
            # Update partial text (ongoing recognition)
            st.session_state.partial_text = result["text"]
            
        elif result["type"] == "final":
            # Add final text (completed utterance)
            if st.session_state.full_text:
                st.session_state.full_text += " " + result["text"]
            else:
                st.session_state.full_text = result["text"]
            st.session_state.partial_text = ""
            
        elif result["type"] == "error":
            # Display error
            st.error(f"🚨 **Recognition Error:** {result['text']}")
            st.session_state.is_recording = False
            
        elif result["type"] == "status":
            # Show status update
            st.sidebar.info(result["text"])
            
    except queue.Empty:
        break

# Auto-refresh while recording to show live updates
if st.session_state.is_recording or message_processed:
    time.sleep(0.1)  # Small delay to prevent excessive refreshing
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
### 🎯 About This Demo

This is a **comprehensive demonstration** of WhisperBoard's speech recognition capabilities:

- **🎙️ Real-time Processing:** Your speech is transcribed as you speak
- **📁 File Processing:** Upload WAV files for batch transcription
- **🔒 100% Private:** All processing happens locally on your device
- **🌐 Multi-language:** Supports English, Hindi, and Telugu recognition
- **⚡ Fast & Accurate:** Powered by the Vosk speech recognition toolkit

**Built with ❤️ by Team Tokenizer's** | [GitHub Repository](https://github.com/preetham-22/WhisperBoard)
""")
