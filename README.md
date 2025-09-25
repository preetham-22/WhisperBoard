# 🎤 WhisperBoard
**A Privacy-First Speech-to-Text Keyboard for Ubuntu Touch/Lomiri OS**

*Built for the Pragna National Level Open-Source Hackathon*

---

## 🌟 Key Features

WhisperBoard is an innovative **offline speech-to-text keyboard application** designed specifically for **Ubuntu Touch/Lomiri OS**, delivering:

### Core Functionality
- 🎯 **Native Ubuntu Touch Integration** - Built using QML and Python with proper Lomiri OS frameworks
- 🔒 **Privacy-First Design** - All speech processing happens locally using Vosk AI models
- 🌍 **Multi-Language Support** - Supports English, Hindi, and other languages through Vosk models  
- 📱 **Mobile-Optimized Interface** - Touch-friendly QML interface designed for smartphone usage
- ⚡ **Offline Operation** - No internet connection required for speech recognition
- 🔐 **AppArmor Security** - Proper Ubuntu Touch security sandbox integration

### Technical Innovation
- **Open-Source Stack**: Vosk + QML + Python + Clickable build system
- **Cross-Architecture**: Universal (`all`) package supporting multiple device types
- **Professional Build**: Complete Ubuntu Touch application with proper manifest, desktop integration, and security profiles

---

## 🏗️ How to Build

The WhisperBoard Ubuntu Touch application is built using the **Clickable framework** in a **GitHub Codespace environment**. This approach overcame local development challenges and enabled successful compilation.

### Prerequisites
- GitHub Codespace with Ubuntu environment
- Clickable 8.5.0+ framework
- Ubuntu Touch development dependencies

### Build Process
1. **Clone the repository** in a GitHub Codespace
2. **Navigate to the app directory**: `cd whisperboard/`
3. **Install dependencies**: Ubuntu Touch dev tools, Qt5, CMake
4. **Build the application**: `clickable build --container-mode`
5. **Package location**: `build/all/app/whisperboard.preetham22_1.0.0_all.click`

### Installation on Ubuntu Touch
```bash
# Install the .click package on Ubuntu Touch device
pkcon install-local whisperboard.preetham22_1.0.0_all.click
```

---

## 📖 The Hackathon Journey: From Vision to Reality

### 🎯 **Original Vision: Ubuntu Touch Keyboard**
WhisperBoard began with an ambitious goal: create a **privacy-first speech-to-text keyboard** for the Ubuntu Touch mobile operating system. The vision was to fill a gap in the Lomiri OS ecosystem while prioritizing user privacy through offline processing.

### 🚧 **Initial Roadblocks: Local Development Challenges**
The project immediately encountered significant technical hurdles:
- **Environment Setup Complexity**: Ubuntu Touch development requires specific toolchains, Qt versions, and build systems
- **Dependency Conflicts**: Local installation of Clickable framework faced Docker compatibility issues
- **Hardware Limitations**: Testing required Ubuntu Touch devices or complex emulator setups

### 🔄 **Strategic Pivot: Streamlit Proof of Concept**
Faced with these challenges, the project pivoted to demonstrate core functionality:
- **Technology Validation**: Built a **Streamlit web application** to prove Vosk integration works
- **Multi-Language Testing**: Successfully implemented English and Hindi speech recognition
- **Privacy Architecture**: Demonstrated offline processing capabilities
- **User Interface Design**: Created an intuitive speech input interface

*This pivot proved the fundamental technology stack while maintaining project momentum during the hackathon timeline.*

### 🌟 **Breakthrough: Cloud Development Success**
The final breakthrough came through **professional cloud development practices**:
- **GitHub Codespaces**: Leveraged Microsoft's cloud development environment
- **Container Bypass**: Used `--container-mode` to avoid Docker compatibility issues
- **Native Dependencies**: Installed Ubuntu Touch build tools directly in the cloud environment
- **Successful Compilation**: Achieved full .click package generation

### 🎉 **Final Achievement: Complete Ubuntu Touch Application**
The project successfully delivered its original vision:
- ✅ **Native Lomiri Application**: Full Ubuntu Touch integration
- ✅ **Privacy-Preserved**: Offline Vosk speech recognition
- ✅ **Professional Build**: Complete .click package ready for installation
- ✅ **Technical Innovation**: Overcame significant development environment challenges

### 🧠 **Key Learnings**
1. **Resilience in Development**: When local environments fail, cloud solutions can provide the breakthrough
2. **Technology Validation**: Proof-of-concept implementations help validate core technical approaches
3. **Platform-Specific Challenges**: Mobile OS development requires specialized toolchains and expertise
4. **Community Solutions**: Open-source ecosystems like Ubuntu Touch benefit from community-driven development

---

## 🚀 Project Structure

```
WhisperBoard/
├── 📱 whisperboard/              # Ubuntu Touch Application
│   ├── qml/Main.qml             # QML user interface
│   ├── src/example.py           # Python backend logic
│   ├── assets/logo.svg          # App icon and assets
│   ├── manifest.json.in         # App metadata template
│   ├── clickable.yaml           # Build configuration
│   ├── whisperboard.apparmor    # Security profile
│   └── build/all/app/           # Build output directory
│       └── whisperboard.preetham22_1.0.0_all.click  # 📦 Final Package
├── 🌐 Streamlit App/            # Web-based proof of concept
│   ├── app.py                   # Streamlit application
│   ├── requirements.txt         # Python dependencies
│   └── model/ & model-hi/       # Vosk AI models (downloaded separately)
└── 📚 Documentation/            # Project documentation
```

---

## 🏆 Hackathon Achievement

**WhisperBoard** represents a complete journey from concept to working Ubuntu Touch application, demonstrating:

- **Technical Innovation**: Privacy-first mobile speech recognition
- **Problem-Solving**: Overcoming complex development environment challenges  
- **Platform Expertise**: Successfully building for a specialized mobile OS
- **Professional Development**: Using cloud-based development workflows to deliver results

*The project showcases both the original Lomiri keyboard application and the Streamlit proof-of-concept that validated the core technology during development challenges.*

---

## 📞 Contact & Submission

**Developer**: Gade Joseph Preetham Reddy  
**Email**: preethamreddy2226@gmail.com  
**GitHub**: [@preetham-22](https://github.com/preetham-22)  
**Repository**: [WhisperBoard](https://github.com/preetham-22/WhisperBoard)

**Hackathon**: Pragna National Level Open-Source Hackathon  
**Final Package**: `whisperboard.preetham22_1.0.0_all.click` ✅
