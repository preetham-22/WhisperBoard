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
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = {}
if 'audio_devices_checked' not in st.session_state:
    st.session_state.audio_devices_checked = False
if 'available_devices' not in st.session_state:
    st.session_state.available_devices = []

# --- AUDIO DEVICE DETECTION ---
def check_audio_devices():
    """Check available audio input devices"""
    try:
        devices = sd.query_devices()
        input_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        
        st.session_state.available_devices = input_devices
        st.session_state.audio_devices_checked = True
        
        return len(input_devices) > 0, input_devices
    
    except Exception as e:
        st.session_state.audio_devices_checked = True
        return False, str(e)

# --- MODEL LOADING ---
def load_vosk_model(model_path, language):
    """Load Vosk model with error handling"""
    try:
        if not os.path.exists(model_path):
            return False, f"Model directory not found: {model_path}"
        
        # Check if model files exist
        required_files = ['am/final.mdl', 'graph/HCLr.fst', 'graph/Gr.fst']
        for file_path in required_files:
            full_path = os.path.join(model_path, file_path)
            if not os.path.exists(full_path):
                return False, f"Missing model file: {full_path}"
        
        model = vosk.Model(model_path)
        st.session_state.models_loaded[language] = model
        return True, f"✅ {language} model loaded successfully"
    
    except Exception as e:
        st.session_state.models_loaded[language] = None
        return False, f"❌ Error loading {language} model: {str(e)}"

# --- VOSK WORKER THREAD ---
def vosk_worker(model, language, text_queue_ref, stop_event, device_index=None):
    """Enhanced Vosk worker with better error handling"""
    try:
        samplerate = 16000
        audio_q = queue.Queue()

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}", file=sys.stderr)
            audio_q.put(bytes(indata))

        # Use specific device if provided
        device_config = {'device': device_index} if device_index is not None else {}
        
        with sd.RawInputStream(samplerate=samplerate, 
                               blocksize=8000,
                               dtype='int16',
                               channels=1, 
                               callback=audio_callback,
                               **device_config):
            
            rec = vosk.KaldiRecognizer(model, samplerate)
            rec.SetWords(True)
            print(f"INFO: [{language}] Vosk Worker is now listening on device {device_index}.")
            
            # Send ready signal
            text_queue_ref.put({"type": "status", "text": f"🎙️ Listening with {language} model..."})
            
            while not stop_event.is_set():
                try:
                    data = audio_q.get(timeout=0.1)
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        if result.get('text'):
                            text_queue_ref.put({"type": "final", "text": result['text']})
                    else:
                        partial_result = json.loads(rec.PartialResult())
                        if partial_result.get('partial'):
                            text_queue_ref.put({"type": "partial", "text": partial_result['partial']})
                except queue.Empty:
                    pass
        
        print(f"INFO: [{language}] Vosk Worker has gracefully stopped.")
        text_queue_ref.put({"type": "status", "text": "⏹️ Recording stopped."})
        
    except Exception as e:
        error_message = f"ERROR: Error in Vosk worker for {language}: {e}"
        print(error_message, file=sys.stderr)
        text_queue_ref.put({"type": "error", "text": error_message})

# --- Streamlit User Interface ---
st.set_page_config(layout="wide", page_title="WhisperBoard - Local Edition")
st.title("🎤 WhisperBoard - Local Edition")
st.markdown("A privacy-focused, multi-language speech recognition app powered by **Vosk**. Built for the Pragna Hackathon.")

# Check system compatibility
st.sidebar.header("🔧 System Status")

# Check audio devices
if not st.session_state.audio_devices_checked:
    with st.spinner("Checking audio devices..."):
        devices_ok, devices_info = check_audio_devices()

if st.session_state.audio_devices_checked:
    if st.session_state.available_devices:
        st.sidebar.success(f"✅ Found {len(st.session_state.available_devices)} audio input device(s)")
        
        # Device selection
        device_names = ["Default"] + [dev['name'] for dev in st.session_state.available_devices]
        selected_device_name = st.sidebar.selectbox(
            "Audio Input Device", 
            device_names,
            disabled=st.session_state.is_recording
        )
        
        if selected_device_name == "Default":
            selected_device_index = None
        else:
            selected_device_index = next(
                dev['index'] for dev in st.session_state.available_devices 
                if dev['name'] == selected_device_name
            )
    else:
        st.sidebar.error("❌ No audio input devices found")
        st.error("🎤 **No microphone detected!**\n\nPlease ensure:")
        st.error("• Your microphone is connected and not muted")
        st.error("• Audio drivers are properly installed")
        st.error("• You've granted microphone permissions")
        st.stop()

# Language and model selection
st.sidebar.header("🌐 Language Settings")
MODELS = {
    "English (US)": "model",
    "Hindi (हिन्दी)": "model-hi"
}

language = st.sidebar.selectbox(
    "Select Language", 
    list(MODELS.keys()), 
    disabled=st.session_state.is_recording
)

# Load model if not already loaded
model_path = MODELS[language]
if language not in st.session_state.models_loaded:
    with st.spinner(f"Loading {language} model..."):
        success, message = load_vosk_model(model_path, language)
        if success:
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)
            st.error(f"**Model Loading Failed**: {message}")
            
            if "not found" in message.lower():
                st.info("💡 **Download Vosk Models:**")
                if language == "English (US)":
                    st.code("""
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
mv vosk-model-en-us-0.22 model
                    """)
                else:
                    st.code("""
wget https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip
unzip vosk-model-hi-0.22.zip
mv vosk-model-hi-0.22 model-hi
                    """)
            st.stop()
else:
    if st.session_state.models_loaded[language]:
        st.sidebar.success(f"✅ {language} model ready")
    else:
        st.sidebar.error(f"❌ {language} model failed to load")
        st.stop()

# Recording controls
st.sidebar.header("🎙️ Recording Controls")
model_ready = st.session_state.models_loaded.get(language) is not None

if st.sidebar.button(
    "🔴 Start Recording" if not st.session_state.is_recording else "⏹️ Stop Recording",
    disabled=not model_ready
):
    if not st.session_state.is_recording:
        # Start recording
        st.session_state.is_recording = True
        st.session_state.stop_event.clear()
        st.session_state.full_text = ""
        st.session_state.partial_text = ""
        
        model = st.session_state.models_loaded[language]
        device_idx = selected_device_index if 'selected_device_index' in locals() else None
        
        worker_thread = threading.Thread(
            target=vosk_worker, 
            args=(model, language, st.session_state.text_queue, st.session_state.stop_event, device_idx)
        )
        st.session_state.vosk_worker_thread = worker_thread
        worker_thread.start()
    else:
        # Stop recording
        st.session_state.is_recording = False
        if st.session_state.vosk_worker_thread:
            st.session_state.stop_event.set()
            st.session_state.vosk_worker_thread.join(timeout=2)
        st.session_state.partial_text = ""
    
    st.rerun()

# Status display
if st.session_state.is_recording:
    st.sidebar.info("🎙️ Recording... Speak into your microphone!")
elif model_ready:
    st.sidebar.success("✅ Ready to record")
else:
    st.sidebar.warning("⚠️ Model not loaded")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Live Transcription")
    
    # Display transcribed text
    display_text = st.session_state.full_text
    if st.session_state.partial_text:
        display_text += " " + st.session_state.partial_text + "_"
    
    st.text_area(
        "Recognized Speech", 
        value=display_text.strip(), 
        height=300,
        key="transcribed_text_display",
        help="Speak into your microphone to see real-time transcription"
    )
    
    # Clear button
    if st.button("🗑️ Clear Text"):
        st.session_state.full_text = ""
        st.session_state.partial_text = ""
        st.rerun()

with col2:
    st.header("ℹ️ Information")
    
    st.subheader("Current Setup")
    st.write(f"**Language**: {language}")
    st.write(f"**Model**: {model_path}")
    if 'selected_device_name' in locals():
        st.write(f"**Audio Device**: {selected_device_name}")
    st.write(f"**Status**: {'🔴 Recording' if st.session_state.is_recording else '⏸️ Idle'}")
    
    st.subheader("Instructions")
    st.write("1. Select your preferred language")
    st.write("2. Choose audio input device")
    st.write("3. Click 'Start Recording'")
    st.write("4. Speak clearly into microphone")
    st.write("5. Watch real-time transcription")
    
    st.subheader("Tips for Better Recognition")
    st.write("• Speak clearly and at normal pace")
    st.write("• Minimize background noise")
    st.write("• Use a good quality microphone")
    st.write("• Stay close to the microphone")

# Process text queue
while not st.session_state.text_queue.empty():
    try:
        result = st.session_state.text_queue.get_nowait()
        
        if result["type"] == "partial":
            st.session_state.partial_text = result["text"]
        elif result["type"] == "final":
            if st.session_state.full_text:
                st.session_state.full_text += " " + result["text"]
            else:
                st.session_state.full_text = result["text"]
            st.session_state.partial_text = ""
        elif result["type"] == "error":
            st.error(f"🚨 **Error**: {result['text']}")
        elif result["type"] == "status":
            st.sidebar.info(result["text"])
        
        st.rerun()
    except queue.Empty:
        break

# Auto-refresh while recording
if st.session_state.is_recording:
    time.sleep(0.1)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
### 🎯 About WhisperBoard

WhisperBoard is a privacy-focused speech-to-text application that runs entirely on your local machine. 
All voice processing happens offline using the Vosk speech recognition toolkit.

**Privacy Features:**
- ✅ **100% Offline**: No internet connection required
- ✅ **Local Processing**: Voice data never leaves your device
- ✅ **Open Source**: Fully transparent and auditable code
- ✅ **Multi-language**: Support for English and Hindi

Built with ❤️ by **Gade Joseph Preetham Reddy** | [GitHub Repository](https://github.com/preetham-22/WhisperBoard)
""")