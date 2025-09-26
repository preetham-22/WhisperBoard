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
    echo To download the models:
    echo 1. Visit: https://github.com/preetham-22/WhisperBoard/releases
    echo 2. Download WhisperBoard-Models.zip
    echo 3. Extract the zip file in this directory
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