import streamlit as st
import vosk
import sounddevice as sd
import queue
import json
import threading
import sys
import time

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

# --- VOSK WORKER THREAD ---
def vosk_worker(model_path, language, text_queue_ref, stop_event):
    try:
        model = vosk.Model(model_path)
        samplerate = 16000
        audio_q = queue.Queue()

        def audio_callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            audio_q.put(bytes(indata))

        with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                               device=None, dtype='int16',
                               channels=1, callback=audio_callback):
            rec = vosk.KaldiRecognizer(model, samplerate)
            rec.SetWords(True)
            print(f"INFO: [{language}] Vosk Worker is now listening.")
            
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
    except Exception as e:
        error_message = f"ERROR: Error in Vosk worker for {language}: {e}"
        st.session_state.text_queue.put({"type": "error", "text": error_message})

# --- Streamlit User Interface ---
st.set_page_config(layout="wide", page_title="WhisperBoard")
st.title("🎤 WhisperBoard")
st.markdown("A privacy-focused, multi-language speech recognition app powered by **Vosk**. Built for the Pragna Hackathon.")

st.sidebar.header("Controls")
MODELS = {
    "English (US)": "model",
    "Hindi (हिन्दी)": "model-hi"
}
language = st.sidebar.selectbox("Select Language", list(MODELS.keys()), disabled=st.session_state.is_recording)

if st.sidebar.button("🔴 Start Recording" if not st.session_state.is_recording else "⏹️ Stop Recording"):
    if not st.session_state.is_recording:
        st.session_state.is_recording = True
        st.session_state.stop_event.clear()
        model_path = MODELS[language]
        worker_thread = threading.Thread(
            target=vosk_worker, 
            args=(model_path, language, st.session_state.text_queue, st.session_state.stop_event)
        )
        st.session_state.vosk_worker_thread = worker_thread
        worker_thread.start()
    else:
        st.session_state.is_recording = False
        if st.session_state.vosk_worker_thread:
            st.session_state.stop_event.set()
            st.session_state.vosk_worker_thread.join(timeout=1)
        st.session_state.partial_text = ""
    st.rerun()

if st.session_state.is_recording:
    st.sidebar.info("Recording started... Speak into your microphone.")
else:
    st.sidebar.success("Ready to record.")

st.header("Transcription")
display_text = st.session_state.full_text + " " + st.session_state.partial_text
st.text_area("Recognized Text", value=display_text.strip(), height=300, key="transcribed_text_display")

while not st.session_state.text_queue.empty():
    result = st.session_state.text_queue.get()
    if result["type"] == "partial":
        st.session_state.partial_text = result["text"]
    elif result["type"] == "final":
        st.session_state.full_text += " " + result["text"]
        st.session_state.partial_text = ""
    elif result["type"] == "error":
        st.error(result["text"])
    st.rerun()

if st.session_state.is_recording:
    time.sleep(0.1)
    st.rerun()

st.markdown("---")
st.write("Built with ❤️ by **Gade Joseph Preetham Reddy** | [GitHub Repository](https://github.com/preetham-22/WhisperBoard)")
