# WhisperBoard 🎤

A privacy-focused, multi-language, real-time speech-to-text keyboard for the Lomiri (U### 📁 Project Structure
```
WhisperBoard/
├── whisperboard/           # Clickable app source directory
│   ├── clickable.yaml      # Clickable configuration
│   ├── manifest.json       # App metadata
│   └── ...                 # Other QML/Python files
├── model-English/          # English (US) Vosk model (download required)
├── model-Hindi/            # Hindi (हिन्दी) Vosk model (download required)  
├── model-Telugu/           # Telugu (తెలుగు) Vosk model (download required)
├── app.py                  # Streamlit web application
├── test_audio_recognition.py # Model testing script
├── test_telugu_model.py    # Telugu model debugging script
├── requirements.txt        # Python dependencies
├── LICENSE                 # AGPL-3.0 License
└── README.md               # You are here!
```

### 🤖 Language Models

WhisperBoard uses specialized Vosk models for each supported language:

| Language | Model Directory | Features |
|----------|-----------------|----------|
| **English (US)** | `model-English/` | High accuracy, fast recognition, partial results |
| **Hindi (हिन्दी)** | `model-Hindi/` | Devanagari script support, partial results |  
| **Telugu (తెలుగు)** | `model-Telugu/` | Telugu script support, complete phrase recognition |

**Note:** Model files are large (100+ MB each) and are distributed separately via GitHub Releases.OS. This project was built for the **Pragna National Level Open-Source Hackathon**.

### ✨ Key Features

* **Real-time Transcription:** Converts speech to text live on the device.
* **Multi-Language Support:** Supports English, Hindi, and Telugu with dedicated Vosk models.
* **100% Offline & Private:** All AI processing happens on the device using the Vosk toolkit, ensuring user voice data remains completely private.
* **Open Source:** Built entirely with free and open-source tools.
* **Easy Model Distribution:** Pre-trained models available as downloadable packages.

### � Final Status

This project successfully achieved its primary goal. The final deliverable is a **`.click`** application package, ready for installation on a Lomiri (Ubuntu Touch) device.

### 🚀 The Hackathon Journey: A Story of Resilience

This project's story is a testament to agile problem-solving and resilience in the face of significant technical challenges.

1.  **The Initial Goal:** The original challenge was to build a virtual keyboard directly for the Lomiri OS using the `clickable` toolchain.

2.  **The First Roadblock:** Development on a Windows + WSL2 environment was halted by critical, show-stopping bugs in the `clickable` toolchain and insurmountable networking issues between the host and the emulator.

3.  **The Strategic Pivot:** To meet the hackathon's core AI requirements and deliver a functional product, the project was pivoted to a Streamlit-based web application. This demonstrated the core Vosk AI engine and its multi-language capabilities successfully.

4.  **The Final Push:** After overcoming numerous local environment failures (including unstable Virtual Machines and deep-seated Docker bugs), development was moved to a professional cloud-based environment using **GitHub Codespaces**. In this stable environment, the original goal was achieved, and the native Lomiri keyboard application was successfully built.

This journey highlights a crucial real-world engineering skill: adapting to broken tools and environments to deliver a high-quality product.

### 🧠 Model Performance Improvement

Beyond the core application, a custom Language Model (LM) was successfully trained using the **KenLM** toolkit. This new model (`lm.arpa`) was trained on a custom corpus of technical jargon ("Vosk", "Streamlit", "Lomiri", etc.) and is designed to be integrated into the Vosk model to significantly improve the recognition accuracy for domain-specific terms.

## 📦 How to Install and Use

Ready to use WhisperBoard? Follow these simple steps:

### For Streamlit Web Application:

#### 1. Download Model Files
Visit the [Releases](https://github.com/preetham-22/WhisperBoard/releases) page and download the **WhisperBoard-Models.zip** file containing all language models.

#### 2. Extract Models
Extract the downloaded zip file to your project directory. You should have:
```
WhisperBoard/
├── model-English/     # English (US) language model
├── model-Hindi/       # Hindi (हिन्दी) language model
├── model-Telugu/      # Telugu (తెలుగు) language model
└── app.py            # Main application file
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Application
```bash
streamlit run app.py
```

### For Lomiri/Ubuntu Touch Users:

#### 1. Download the Package
Visit the [Releases](https://github.com/preetham-22/WhisperBoard/releases) page of this repository and download the latest `.click` package file (e.g., `whisperboard.preetham22_1.0.0_all.click`).

### 2. Transfer to Device
Use the Android Debug Bridge (adb) to transfer the package to your device's Downloads folder:

```bash
adb push whisperboard.preetham22_1.0.0_all.click /home/phablet/Downloads/
```

### 3. Install the App
On your Lomiri device, open a terminal and run the following command to install the package:

```bash
pkcon install-local --allow-untrusted ~/Downloads/whisperboard.preetham22_1.0.0_all.click
```

### 4. Enable the Keyboard
Finally, enable WhisperBoard in your system settings:
1. Navigate to **System Settings** → **Keyboard** → **Manage**
2. Find "WhisperBoard" in the list
3. Toggle it **ON** to activate the speech-to-text keyboard

That's it! You can now use WhisperBoard for real-time speech-to-text input across all your applications.

### 🛠️ How to Build

This project is configured to be built in a cloud development environment.

1.  **Launch in GitHub Codespaces:** Fork this repository and launch it in a new GitHub Codespace.
2.  **Install Dependencies:** The Codespace will provide a clean Ubuntu environment. Install the necessary tools:
    ```bash
    sudo apt-get update && sudo apt-get install -y docker.io pipx adb
    pipx install clickable-ut
    pipx ensurepath
    ```
3.  **Build the App:** Navigate into the `whisperboard` sub-directory and run the build command:
    ```bash
    clickable build
    ```
    This will generate the final `.click` package in the `build` directory.

### � Project Structure
```
WhisperBoard/
├── whisperboard/           # Clickable app source directory
│   ├── clickable.yaml      # Clickable configuration
│   ├── manifest.json       # App metadata
│   └── ...                 # Other QML/Python files
├── model/                  # Placeholder for Vosk English model
├── model-hi/               # Placeholder for Vosk Hindi model
├── app.py                  # Original Streamlit PoC
├── LICENSE                 # AGPL-3.0 License
└── README.md               # You are here!
```

### About the Developer

This project was built with ❤️ by **Gade Joseph Preetham Reddy**.
