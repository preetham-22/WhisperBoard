🎤 WhisperBoard
A privacy-focused, multi-language speech recognition web app powered by Vosk. Built for the Pragna National Level Open-Source Hackathon.

Getting Started: Running Locally
Important Note on Deployment: Deploying real-time microphone applications to generic cloud platforms (like Streamlit Cloud or Render) is a complex technical challenge due to missing system-level audio dependencies (like PortAudio) and browser security models.

Therefore, the best and most reliable way to experience the full power of WhisperBoard is to run it on your local machine, where it has direct access to your microphone hardware.

This guide will walk you through the setup process.

1. Prerequisites
Python 3.9+: Make sure you have a recent version of Python installed. You can download it from python.org.

Git: You'll need Git to clone the repository. You can download it from git-scm.com.

2. Clone the Repository
First, open your terminal or command prompt and clone this repository to your local machine:

git clone [https://github.com/preetham-22/WhisperBoard-Final-Submission.git](https://github.com/preetham-22/WhisperBoard-Final-Submission.git)
cd WhisperBoard-Final-Submission

3. Download the Vosk AI Models
The AI models are too large to be stored on GitHub and must be downloaded manually. The .gitignore file is configured to ignore these folders.

English Model (128 MB):

Go to the Vosk Models Page.

Download the model named vosk-model-en-us-0.22-lgraph.

Unzip the file and rename the resulting folder to just model.

Place this model folder inside your cloned WhisperBoard-Final-Submission directory.

Hindi Model (50 MB):

From the same page, download the model named vosk-model-hi-0.22.

Unzip the file and rename the resulting folder to model-hi.

Place this model-hi folder inside your project directory.

Your final folder structure should look like this:

WhisperBoard-Final-Submission/
├── model/            <-- Your English model files
├── model-hi/         <-- Your Hindi model files
├── app.py
├── requirements.txt
└── README.md

4. Install Required Packages
It is highly recommended to use a Python virtual environment to keep your project dependencies isolated.

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all the required Python libraries from the list
pip install -r requirements.txt

5. Run the Application
You're all set! To run the app, use the following command in your terminal:

streamlit run app.py
