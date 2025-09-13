🎤 WhisperBoard
A privacy-focused, multi-language speech recognition web app powered by Vosk. Built for the Pragna National Level Open-Source Hackathon.

Getting Started: Running Locally
Important Note on Deployment: Deploying real-time microphone applications to generic cloud platforms is a complex technical challenge due to missing system-level audio dependencies and browser security models.

Therefore, the best and most reliable way to experience the full power of WhisperBoard is to run it on your local machine, where it has direct access to your microphone hardware.

This guide will walk you through the entire setup process from scratch.

1. Prerequisites
Python 3.9+: Make sure you have a recent version of Python installed. You can download it from python.org.

Git: You'll need Git to get the code. You can download it from git-scm.com.

2. How to Clone This Repository
"Cloning" is how you download a project from GitHub.

Go to the main page of this GitHub repository: https://github.com/preetham-22/WhisperBoard

Click the green < > Code button.

Make sure the HTTPS tab is selected, and click the copy icon to copy the repository URL.

Now, open your terminal or command prompt, navigate to where you want to save the project, and run the following command:

git clone [https://github.com/preetham-22/WhisperBoard.git](https://github.com/preetham-22/WhisperBoard.git)

This will create a WhisperBoard folder. Navigate into it:

cd WhisperBoard

3. Download the Vosk AI Models
The AI models are too large to be stored on GitHub and must be downloaded manually. The .gitignore file is configured to ignore these folders.

English Model (128 MB):

Go to the Vosk Models Page.

Download the model named vosk-model-en-us-0.22-lgraph.

Unzip the file and rename the resulting folder to just model.

Place this model folder inside your cloned WhisperBoard directory.

Hindi Model (50 MB):

From the same page, download the model named vosk-model-hi-0.22.

Unzip the file and rename the resulting folder to model-hi.

Place this model-hi folder inside your project directory.

Your final folder structure should look like this:

<img width="938" height="236" alt="image" src="https://github.com/user-attachments/assets/32201695-3682-4335-a1e1-c11525d285ab" />

4. How to Install the Required Packages
It is highly recommended to use a Python virtual environment to keep your project dependencies isolated.


Create a Virtual Environment:
From your terminal, inside the WhisperBoard folder, run:

**python -m venv venv**

Activate the Virtual Environment:


On Windows:

**venv\Scripts\activate**


On macOS/Linux:

**source venv/bin/activate**


Install Libraries:
Now, with your virtual environment active, install all the required Python libraries with a single command:

**pip install -r requirements.txt**


5. How to Run the Application
You're all set! To launch the app, run the following command in your terminal:

**streamlit run app.py**
