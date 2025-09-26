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

# Function to download and setup a model
download_model() {
    local model_name=$1
    local model_url=$2
    local model_dir=$3
    
    echo "📥 Downloading $model_name model..."
    wget -O "${model_name}.zip" "$model_url"
    
    if [ $? -eq 0 ]; then
        echo "📦 Extracting $model_name model..."
        unzip -q "${model_name}.zip"
        
        # Find the extracted directory (it might have a different name)
        extracted_dir=$(find . -maxdepth 1 -type d -name "*$(echo $model_name | tr '[:upper:]' '[:lower:]')*" -not -name "model-*" | head -1)
        
        if [ -n "$extracted_dir" ]; then
            mv "$extracted_dir" "$model_dir"
            echo "✅ $model_name model installed to $model_dir"
        else
            echo "⚠️ Could not find extracted directory for $model_name"
        fi
        
        # Clean up zip file
        rm -f "${model_name}.zip"
    else
        echo "❌ Failed to download $model_name model"
        return 1
    fi
}

# Check for model files
echo ""
echo "🔍 Checking for model files..."

models=("model-English" "model-Hindi" "model-Telugu")
model_urls=(
    "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip"  
    "https://alphacephei.com/vosk/models/vosk-model-te-0.22.zip"
)
model_names=("English" "Hindi" "Telugu")

missing_models=()
missing_indices=()

for i in "${!models[@]}"; do
    model="${models[$i]}"
    if [ -d "$model" ]; then
        echo "✅ $model found"
    else
        echo "❌ $model not found"
        missing_models+=("$model")
        missing_indices+=($i)
    fi
done

if [ ${#missing_models[@]} -gt 0 ]; then
    echo ""
    echo "⚠️ Missing model directories: ${missing_models[*]}"
    echo ""
    
    # Check if wget is available
    if ! command -v wget &> /dev/null; then
        echo "❌ wget is required to download models automatically."
        echo ""
        echo "Please install wget or download models manually:"
        for i in "${missing_indices[@]}"; do
            echo "  ${model_names[$i]}: ${model_urls[$i]}"
        done
        echo ""
        read -p "Press Enter to continue anyway or Ctrl+C to exit..."
    else
        echo "🤖 Would you like to download the missing models automatically? (y/n)"
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            for i in "${missing_indices[@]}"; do
                download_model "${model_names[$i]}" "${model_urls[$i]}" "${models[$i]}"
            done
        else
            echo ""
            echo "Manual download instructions:"
            for i in "${missing_indices[@]}"; do
                echo "  ${model_names[$i]}: ${model_urls[$i]}"
            done
            echo ""
            read -p "Press Enter to continue anyway or Ctrl+C to exit..."
        fi
    fi
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