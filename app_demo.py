import streamlit as st
import vosk
import json
import time
import os

# --- Demo Text Samples ---
DEMO_TEXTS = {
    "English (US)": [
        "Hello world, this is a test of the WhisperBoard speech recognition system.",
        "The quick brown fox jumps over the lazy dog.",
        "This application uses Vosk for offline speech recognition.",
        "Privacy is important, so all processing happens on your device.",
        "Welcome to the future of speech-to-text technology."
    ],
    "Hindi (हिन्दी)": [
        "नमस्ते दुनिया, यह व्हिस्परबोर्ड का परीक्षण है।",
        "यह एक ऑफलाइन भाषा पहचान प्रणाली है।",
        "गोपनीयता हमारी प्राथमिकता है।",
        "सभी प्रसंस्करण आपके डिवाइस पर होता है।",
        "भविष्य की तकनीक का स्वागत है।"
    ]
}

# --- Application State Management ---
if 'is_demo_running' not in st.session_state:
    st.session_state.is_demo_running = False
if 'demo_text' not in st.session_state:
    st.session_state.demo_text = ""
if 'demo_index' not in st.session_state:
    st.session_state.demo_index = 0
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = {}

def load_vosk_model(model_path, language):
    """Load and validate Vosk model"""
    try:
        if not os.path.exists(model_path):
            return False, f"Model path not found: {model_path}"
        
        model = vosk.Model(model_path)
        st.session_state.models_loaded[language] = True
        return True, f"✅ {language} model loaded successfully"
    except Exception as e:
        st.session_state.models_loaded[language] = False
        return False, f"❌ Error loading {language} model: {str(e)}"

def simulate_speech_recognition(text, language):
    """Simulate real-time speech recognition by revealing text word by word"""
    words = text.split()
    partial_text = ""
    
    placeholder = st.empty()
    
    for i, word in enumerate(words):
        if not st.session_state.is_demo_running:
            break
            
        partial_text += word + " "
        
        # Show partial result
        with placeholder.container():
            st.text_area(
                "Real-time Transcription", 
                value=partial_text.strip() + "_", 
                height=200, 
                key=f"demo_partial_{i}"
            )
        
        time.sleep(0.3)  # Simulate typing speed
    
    # Final result
    if st.session_state.is_demo_running:
        with placeholder.container():
            st.text_area(
                "Real-time Transcription", 
                value=partial_text.strip(), 
                height=200, 
                key="demo_final"
            )

# --- Streamlit User Interface ---
st.set_page_config(layout="wide", page_title="WhisperBoard Demo")

# Header
st.title("🎤 WhisperBoard - Demo Mode")
st.markdown("A privacy-focused, multi-language speech recognition app powered by **Vosk**. Built for the Pragna Hackathon.")

# Info banner about demo mode
st.info("🖥️ **Demo Mode Active**: Since this is running in a cloud environment without microphone access, this demo simulates the real-time speech recognition functionality using pre-defined text samples.")

# Sidebar Controls
st.sidebar.header("🎛️ Controls")

MODELS = {
    "English (US)": "model",
    "Hindi (हिन्दी)": "model-hi"
}

language = st.sidebar.selectbox(
    "Select Language", 
    list(MODELS.keys()), 
    disabled=st.session_state.is_demo_running
)

# Model Status Section
st.sidebar.subheader("📊 Model Status")
model_path = MODELS[language]

if language not in st.session_state.models_loaded:
    with st.spinner(f"Loading {language} model..."):
        success, message = load_vosk_model(model_path, language)
        st.sidebar.write(message)
else:
    if st.session_state.models_loaded.get(language, False):
        st.sidebar.success(f"✅ {language} model ready")
    else:
        st.sidebar.error(f"❌ {language} model failed to load")

# Demo Controls
if st.sidebar.button("🎤 Start Demo" if not st.session_state.is_demo_running else "⏹️ Stop Demo"):
    if not st.session_state.is_demo_running:
        if st.session_state.models_loaded.get(language, False):
            st.session_state.is_demo_running = True
            st.session_state.demo_index = 0
            st.rerun()
        else:
            st.sidebar.error("Cannot start demo: Model not loaded")
    else:
        st.session_state.is_demo_running = False
        st.session_state.demo_text = ""
        st.rerun()

if st.session_state.is_demo_running:
    st.sidebar.info("🎙️ Demo running... Simulating speech recognition.")
else:
    st.sidebar.success("✅ Ready to start demo.")

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Transcription Output")
    
    if st.session_state.is_demo_running:
        demo_texts = DEMO_TEXTS[language]
        if st.session_state.demo_index < len(demo_texts):
            current_text = demo_texts[st.session_state.demo_index]
            
            st.subheader(f"Sample {st.session_state.demo_index + 1} of {len(demo_texts)}")
            st.write(f"**Original text**: {current_text}")
            
            # Simulate real-time recognition
            simulate_speech_recognition(current_text, language)
            
            # Move to next sample
            st.session_state.demo_index += 1
            if st.session_state.demo_index >= len(demo_texts):
                st.session_state.is_demo_running = False
                st.success("🎉 Demo completed! All samples processed.")
            
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.is_demo_running = False
    else:
        st.text_area(
            "Real-time Transcription", 
            value="Click 'Start Demo' to see simulated speech recognition...", 
            height=200,
            disabled=True
        )

with col2:
    st.header("📋 Demo Information")
    
    # Show available samples
    st.subheader("Available Samples")
    demo_texts = DEMO_TEXTS[language]
    for i, text in enumerate(demo_texts):
        status = "✅" if not st.session_state.is_demo_running or st.session_state.demo_index > i else "⏳" if st.session_state.demo_index == i else "⏸️"
        st.write(f"{status} **Sample {i+1}**: {text[:50]}...")
    
    # Technical Details
    st.subheader("🔧 Technical Details")
    st.write(f"**Selected Model**: {model_path}")
    st.write(f"**Language**: {language}")
    st.write(f"**Status**: {'Running' if st.session_state.is_demo_running else 'Idle'}")
    
    # Model Information
    if st.session_state.models_loaded.get(language, False):
        st.write("**Model Features**:")
        st.write("- ✅ Offline processing")
        st.write("- ✅ Real-time recognition")
        st.write("- ✅ Privacy-focused")
        st.write("- ✅ No internet required")

# Footer
st.markdown("---")
st.markdown("""
### 🎯 About WhisperBoard

This demo showcases the core functionality of WhisperBoard, a speech-to-text keyboard application designed for Lomiri (Ubuntu Touch) OS. 

**Key Features Demonstrated:**
- ✅ **Multi-language Support**: Switch between English and Hindi models
- ✅ **Real-time Processing**: Simulated word-by-word transcription
- ✅ **Offline Operation**: All processing happens locally using Vosk
- ✅ **Privacy-First**: No data sent to external servers

**Note**: In the actual application running on a device with microphone access, users would speak directly and see their speech converted to text in real-time.
""")

st.write("Built with ❤️ by **Gade Joseph Preetham Reddy** | [GitHub Repository](https://github.com/preetham-22/WhisperBoard)")