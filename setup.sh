#!/bin/bash
# WhisperBoard Installation Script
# This script helps users set up WhisperBoard with model files

echo "🎤 WhisperBoard Setup Script"
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ Python 3 and pip3 found"

# Install requirements
echo ""
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️ requirements.txt not found, installing essential packages..."
    pip3 install streamlit vosk sounddevice
fi

# Check for model files
echo ""
echo "🔍 Checking for model files..."

models=("model-English" "model-Hindi" "model-Telugu")
missing_models=()

for model in "${models[@]}"; do
    if [ -d "$model" ]; then
        echo "✅ $model found"
    else
        echo "❌ $model not found"
        missing_models+=("$model")
    fi
done

if [ ${#missing_models[@]} -gt 0 ]; then
    echo ""
    echo "⚠️ Missing model directories: ${missing_models[*]}"
    echo ""
    echo "To download the models:"
    echo "1. Visit: https://github.com/preetham-22/WhisperBoard/releases"
    echo "2. Download WhisperBoard-Models.zip"
    echo "3. Extract the zip file in this directory"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
else
    echo "✅ All model files found"
fi

echo ""
echo "🚀 Starting WhisperBoard..."
echo "The application will open in your default web browser."
echo "Press Ctrl+C to stop the application."
echo ""

# Start the application
python3 -m streamlit run app.py