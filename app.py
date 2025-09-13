import streamlit as st
import vosk
import queue
import json
import threading
import sys
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# --- Application State Management ---
if 'full_text' not in st.session_state:
    st.session_state.full_text = ""
if 'partial_text' not in st.session_state:
    st.session_state.partial_text = ""

# --- Vosk Audio Processor ---
# This class processes the audio frames from the browser's microphone stream.
class VoskAudioProcessor(AudioProcessorBase):
    def __init__(self, model_path, language):
        self.model_path = model_path
        self.language = language
        self.text_queue = queue.Queue()
        self.stop_event = threading.Event()

    def recv(self, frame):
        # This is the main callback that receives audio from the browser
        # We start the Vosk worker thread here, when the first audio frame arrives.
        if not hasattr(self, 'vosk_thread'):
            self.vosk_thread = threading.Thread(target=self.vosk_worker, args=(frame.sample_rate,))
            self.vosk_thread.start()

        # The audio from the browser is in a different format, so we need to convert it.
        # Vosk needs raw PCM data (mono, 16-bit signed integer).
        pcm_data = frame.to_ndarray(format="s16", layout="mono").tobytes()
        self.audio_queue.put(pcm_data)

        # We must return the audio frame to the browser
        return frame

    def vosk_worker(self, samplerate):
        # This is our AI brain, running in the background.
        try:
            model = vosk.Model(self.model_path)
            rec = vosk.KaldiRecognizer(model, samplerate)
            rec.SetWords(True)
            self.audio_queue = queue.Queue()
            
            print(f"INFO: [{self.language}] Vosk Worker is now listening.")
            
            while not self.stop_event.is_set():
                try:
                    data = self.audio_queue.get(timeout=0.1)
                    
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        if result.get('text'):
                            self.text_queue.put({"type": "final", "text": result['text']})
                    else:
                        partial_result = json.loads(rec.PartialResult())
                        if partial_result.get('partial'):
                            self.text_queue.put({"type": "partial", "text": partial_result['partial']})
                except queue.Empty:
                    pass
            print(f"INFO: [{self.language}] Vosk Worker has stopped.")
        except Exception as e:
            error_message = f"ERROR: Error in Vosk worker for {self.language}: {e}"
            self.text_queue.put({"type": "error", "text": error_message})
            print(error_message, file=sys.stderr)

    def on_ended(self):
        # This is called when the WebRTC connection is closed.
        self.stop_event.set()
        if hasattr(self, 'vosk_thread'):
            self.vosk_thread.join()

# --- Streamlit User Interface ---
st.set_page_config(layout="wide", page_title="WhisperBoard")
st.title("🎤 WhisperBoard")
st.markdown("A privacy-focused, multi-language speech recognition web app. Built for the Pragna Hackathon.")

st.sidebar.header("Controls")
MODELS = {
    "English (US)": "model",
    "Hindi (हिन्दी)": "model-hi"
}
language = st.sidebar.selectbox("Select Language", list(MODELS.keys()))

st.header("Transcription")
text_placeholder = st.empty() # We'll use this to display live text

# The webrtc_streamer component is the core of our web app now
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SEND_ONLY,
    audio_processor_factory=lambda: VoskAudioProcessor(MODELS[language], language),
    media_stream_constraints={"video": False, "audio": True},
)

if not webrtc_ctx.state.playing:
    st.sidebar.success("Ready to record.")
else:
    st.sidebar.info("Recording started... Speak into your microphone.")

# Logic to update the text display
while webrtc_ctx.state.playing:
    if webrtc_ctx.audio_processor:
        try:
            result = webrtc_ctx.audio_processor.text_queue.get(timeout=0.1)
            
            if result["type"] == "partial":
                st.session_state.partial_text = result["text"]
            elif result["type"] == "final":
                st.session_state.full_text += " " + result["text"]
                st.session_state.partial_text = ""
            elif result["type"] == "error":
                st.error(result["text"])
                break
            
            display_text = st.session_state.full_text + " " + st.session_state.partial_text
            text_placeholder.text_area("Recognized Text", value=display_text.strip(), height=300)

        except queue.Empty:
            pass
    else:
        break

st.markdown("---")
st.write("Built with ❤️ by **Gade Joseph Preetham Reddy** | [GitHub Repository](https://github.com/preetham-22/WhisperBoard-Final-Submission)")
