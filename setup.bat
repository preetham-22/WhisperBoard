@echo off
REM WhisperBoard Setup Script for Windows
REM This script helps users set up WhisperBoard with model files

echo 🎤 WhisperBoard Setup Script
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    echo Please install Python from https://python.org and try again.
    pause
    exit /b 1
)

echo ✅ Python found

REM Install requirements
echo.
echo 📦 Installing Python dependencies...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
    echo ✅ Dependencies installed successfully
) else (
    echo ⚠️ requirements.txt not found, installing essential packages...
    python -m pip install streamlit vosk sounddevice
)

REM Check for model files
echo.
echo 🔍 Checking for model files...

set missing_models=

if exist "model-English" (
    echo ✅ model-English found
) else (
    echo ❌ model-English not found
    set missing_models=%missing_models% model-English
)

if exist "model-Hindi" (
    echo ✅ model-Hindi found
) else (
    echo ❌ model-Hindi not found
    set missing_models=%missing_models% model-Hindi
)

if exist "model-Telugu" (
    echo ✅ model-Telugu found  
) else (
    echo ❌ model-Telugu not found
    set missing_models=%missing_models% model-Telugu
)

if not "%missing_models%"=="" (
    echo.
    echo ⚠️ Missing model directories:%missing_models%
    echo.
    echo 📥 To download the models manually, visit:
    echo   English: https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
    echo   Hindi:   https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip
    echo   Telugu:  https://alphacephei.com/vosk/models/vosk-model-te-0.22.zip
    echo.
    echo 💡 Download, extract, and rename the folders to:
    echo   vosk-model-en-us-0.22 → model-English
    echo   vosk-model-hi-0.22    → model-Hindi  
    echo   vosk-model-te-0.22    → model-Telugu
    echo.
    echo 🤖 Or use Python to download automatically:
    echo   python -c "import urllib.request, zipfile, os; [urllib.request.urlretrieve(url, f'{name}.zip') or zipfile.ZipFile(f'{name}.zip').extractall() or os.rename([d for d in os.listdir('.') if name.lower() in d.lower() and os.path.isdir(d) and not d.startswith('model-')][0], f'model-{name}') or os.remove(f'{name}.zip') for name, url in [('English', 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip'), ('Hindi', 'https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip'), ('Telugu', 'https://alphacephei.com/vosk/models/vosk-model-te-0.22.zip')]]"
    echo.
    pause
) else (
    echo ✅ All model files found
)

echo.
echo 🚀 Starting WhisperBoard...
echo The application will open in your default web browser.
echo Press Ctrl+C to stop the application.
echo.

REM Start the application
python -m streamlit run app.py