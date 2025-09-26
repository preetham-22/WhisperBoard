#!/usr/bin/env python3
"""
WhisperBoard Model Downloader
Downloads and sets up Vosk models for WhisperBoard
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

# Model configuration
MODELS = {
    "English": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "directory": "model-English",
        "size": "~50 MB"
    },
    "Hindi": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip", 
        "directory": "model-Hindi",
        "size": "~42 MB"
    },
    "Telugu": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-te-0.22.zip",
        "directory": "model-Telugu", 
        "size": "~45 MB"
    }
}

def download_progress(block_num, block_size, total_size):
    """Display download progress"""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100, (downloaded * 100) // total_size)
        print(f"\r📥 Downloading... {percent}% ({downloaded // (1024*1024)} MB / {total_size // (1024*1024)} MB)", end="")
    else:
        print(f"\r📥 Downloaded {downloaded // (1024*1024)} MB...", end="")

def download_and_extract_model(language, model_info):
    """Download and extract a single model"""
    print(f"\n🔽 Downloading {language} model ({model_info['size']})...")
    
    zip_filename = f"vosk-model-{language.lower()}.zip"
    target_dir = model_info['directory']
    
    try:
        # Download the model
        urllib.request.urlretrieve(model_info['url'], zip_filename, download_progress)
        print(f"\n✅ Downloaded {language} model")
        
        # Extract the zip file
        print(f"📦 Extracting {language} model...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Find the extracted directory
        extracted_dirs = [d for d in os.listdir('.') 
                         if os.path.isdir(d) 
                         and 'vosk-model' in d.lower()
                         and language.lower()[:2] in d.lower()
                         and not d.startswith('model-')]
        
        if extracted_dirs:
            extracted_dir = extracted_dirs[0]
            
            # Remove existing target directory if it exists
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            
            # Rename to target directory
            os.rename(extracted_dir, target_dir)
            print(f"✅ {language} model installed to {target_dir}")
        else:
            print(f"⚠️ Could not find extracted directory for {language} model")
            return False
        
        # Clean up zip file
        os.remove(zip_filename)
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to download {language} model: {str(e)}")
        # Clean up on failure
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

def check_existing_models():
    """Check which models are already present"""
    existing = []
    missing = []
    
    for language, model_info in MODELS.items():
        if os.path.exists(model_info['directory']) and os.path.isdir(model_info['directory']):
            existing.append(language)
        else:
            missing.append(language)
    
    return existing, missing

def main():
    print("🎤 WhisperBoard Model Downloader")
    print("=" * 40)
    
    # Check existing models
    existing, missing = check_existing_models()
    
    if existing:
        print("✅ Found existing models:")
        for lang in existing:
            print(f"   • {lang} ({MODELS[lang]['directory']})")
    
    if not missing:
        print("\n🎉 All models are already installed!")
        return
    
    print(f"\n❌ Missing models: {', '.join(missing)}")
    print(f"📊 Total download size: ~{sum(int(MODELS[lang]['size'].split('~')[1].split(' ')[0]) for lang in missing)} MB")
    
    # Ask user what to download
    print("\nOptions:")
    print("1. Download all missing models")
    print("2. Choose specific models")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Download cancelled by user")
        return
    
    if choice == "1":
        # Download all missing
        to_download = missing
    elif choice == "2":
        # Choose specific models
        print("\nSelect models to download (comma-separated numbers):")
        for i, lang in enumerate(missing, 1):
            print(f"{i}. {lang} ({MODELS[lang]['size']})")
        
        try:
            selections = input("Enter numbers: ").strip().split(',')
            indices = [int(s.strip()) - 1 for s in selections if s.strip().isdigit()]
            to_download = [missing[i] for i in indices if 0 <= i < len(missing)]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
    elif choice == "3":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
        return
    
    if not to_download:
        print("❌ No models selected")
        return
    
    # Download selected models
    print(f"\n🚀 Starting download of {len(to_download)} model(s)...")
    
    success_count = 0
    for language in to_download:
        if download_and_extract_model(language, MODELS[language]):
            success_count += 1
    
    # Summary
    print(f"\n{'='*40}")
    if success_count == len(to_download):
        print(f"🎉 Successfully installed {success_count}/{len(to_download)} models!")
        print("\n🚀 You can now run WhisperBoard:")
        print("   python -m streamlit run app.py")
    else:
        print(f"⚠️ Installed {success_count}/{len(to_download)} models")
        if success_count > 0:
            print("You can still use WhisperBoard with the available models.")

if __name__ == "__main__":
    main()