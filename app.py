import streamlit as st
import vosk
import sounddevice as sd
import queue
import json
import threading
import sys
import time
import os

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
    st.header("📝 Live Transcription")
    
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
        height=400,
        disabled=True,
        help="Live transcription will appear here as you speak"
    )
    
    # Control buttons
    col_clear, col_copy = st.columns(2)
    with col_clear:
        if st.button("🗑️ Clear Text", disabled=st.session_state.is_recording):
            st.session_state.full_text = ""
            st.session_state.partial_text = ""
            st.rerun()
    
    with col_copy:
        if st.session_state.full_text:
            st.download_button(
                label="📋 Download Text",
                data=st.session_state.full_text,
                file_name=f"transcription_{language.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )

with col2:
    st.header("ℹ️ Status")
    
    # Current configuration
    st.subheader("Configuration")
    st.write(f"**Language:** {language}")
    st.write(f"**Model:** {model_path}")
    st.write(f"**Status:** {'🔴 Recording' if st.session_state.is_recording else '⏸️ Idle'}")
    
    # Instructions
    st.subheader("How to Use")
    st.write("1. Select your language")
    st.write("2. Click 'Start Recording'")
    st.write("3. Speak clearly into microphone")
    st.write("4. Watch live transcription")
    st.write("5. Click 'Stop Recording' when done")
    
    # Special note for Telugu
    if language == "Telugu (తెలుగు)":
        st.info("📝 **Telugu Note**: Text appears after complete phrases (no live preview while speaking)")
    
    # Tips
    st.subheader("💡 Tips")
    st.write("• Speak at normal pace")
    st.write("• Minimize background noise")
    st.write("• Use a quality microphone")
    st.write("• Stay close to the microphone")
    
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

This is a **live demonstration** of WhisperBoard's speech recognition capabilities:

- **🎙️ Real-time Processing:** Your speech is transcribed as you speak
- **🔒 100% Private:** All processing happens locally on your device
- **🌐 Multi-language:** Supports English and Hindi recognition
- **⚡ Fast & Accurate:** Powered by the Vosk speech recognition toolkit

**Built with ❤️ by Gade Joseph Preetham Reddy** | [GitHub Repository](https://github.com/preetham-22/WhisperBoard)
""")
