WhisperBoard 🎤
A privacy-focused, multi-language, real-time speech-to-text web application built for the Pragna National Level Open-Source Hackathon.

This project showcases the power of the Vosk offline speech recognition toolkit by wrapping it in a modern, accessible web interface built with Streamlit.

🚀 Live Demo
[Link to your deployed Streamlit App will go here!]

✨ Key Features
Real-time Transcription: See your spoken words converted to text live on screen.

Multi-Language Support: Seamlessly switch between high-accuracy models for English (US) and Hindi (हिन्दी).

100% Offline & Private: All AI processing happens within the app's backend. Your voice data never leaves the server, ensuring complete privacy.

Modern Web Interface: A clean, user-friendly UI built with Streamlit, making the technology accessible to everyone.

Easy to Deploy: Ready to be deployed on platforms like Streamlit Community Cloud.

💻 How to Run Locally
To run WhisperBoard on your local machine, follow these steps:

Clone the repository:

git clone [https://github.com/preetham-22/WhisperBoard.git](https://github.com/preetham-22/WhisperBoard.git)
cd WhisperBoard

Install dependencies:
Make sure you have Python 3.9+ installed, then run:

pip install -r requirements.txt

Download the Vosk Models:

Download the English model (128 MB) and unzip it into a folder named model.

Download the Hindi model (50 MB) and unzip it into a folder named model-hi.

Run the app:

streamlit run app.py

Your browser will open with the app running at http://localhost:8501.

🛠️ The Hackathon Journey: Overcoming Technical Hurdles
This project's story is one of adaptation and resilience.

The initial goal was to implement WhisperBoard as a virtual keyboard for the Lomiri (Ubuntu Touch) OS, as per the hackathon problem statement. The prescribed tool for this was clickable, a FOSS toolchain for building Lomiri apps.

However, during development, I encountered a series of critical, show-stopping bugs in the clickable toolchain on the Windows development environment. My journey involved:

Patching the Toolchain: Manually editing the clickable source code to fix multiple Windows-incompatibility bugs, including:

An AttributeError for os.getuid(), a Linux-only function call.

A FileNotFoundError caused by the tool attempting to run the Linux-only lsmod command.

Multiple ModuleNotFoundError issues due to incorrect relative path imports within the tool itself.

Exploring WSL: Attempting a full development environment pivot to Windows Subsystem for Linux (WSL) to achieve a native environment.

Debugging the Bridge: Facing insurmountable networking challenges (Connection refused, Exec format error) while trying to bridge the ADB (Android Debug Bridge) connection between the Windows-hosted emulator and the WSL-hosted development tools.

After exhausting all documented solutions and receiving mentor advice that confirmed the complexity of the issue, and with the submission deadline approaching, I made a critical strategic decision: to pivot the project's frontend from a Lomiri-specific app to a robust, shareable Streamlit web application.

This pivot allowed me to successfully deliver a project that not only meets the core AI and multi-language requirements of the problem statement but also demonstrates a crucial real-world engineering skill: knowing when a tool is broken and having the agility to adapt and deliver a high-quality product using a more reliable technology stack.

📂 Project Structure
WhisperBoard/
├── model/            # Vosk English model files
├── model-hi/         # Vosk Hindi model files
├── app.py            # The main Streamlit application script
├── requirements.txt  # Python dependencies for the project
└── README.md         # You are here!

About the Developer
This project was built with ❤️ by Gade Joseph Preetham Reddy.

GitHub Profile

LinkedIn Profile <!-- Add your LinkedIn URL! -->