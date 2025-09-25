#!/usr/bin/env python3
"""
Audio Device Diagnostic Script for WhisperBoard
This script helps diagnose audio device issues and test microphone access.
"""

import sys
import traceback

def test_sounddevice():
    """Test sounddevice library and list available devices"""
    try:
        import sounddevice as sd
        print("✅ sounddevice library imported successfully")
        
        print("\n🎤 Available Audio Devices:")
        print("-" * 50)
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append("INPUT")
            if device['max_output_channels'] > 0:
                device_type.append("OUTPUT")
            
            print(f"Device {i}: {device['name']}")
            print(f"  Type: {' & '.join(device_type)}")
            print(f"  Channels: IN={device['max_input_channels']}, OUT={device['max_output_channels']}")
            print(f"  Sample Rate: {device['default_samplerate']} Hz")
            print()
        
        # Test default input device
        try:
            default_device = sd.query_devices(kind='input')
            print(f"✅ Default input device: {default_device['name']}")
            return True
        except Exception as e:
            print(f"❌ Error accessing default input device: {e}")
            return False
            
    except ImportError:
        print("❌ sounddevice library not installed")
        print("Install with: pip install sounddevice")
        return False
    except Exception as e:
        print(f"❌ Error testing sounddevice: {e}")
        traceback.print_exc()
        return False

def test_vosk():
    """Test Vosk library"""
    try:
        import vosk
        print("✅ Vosk library imported successfully")
        
        # Test model loading
        import os
        models_to_test = [
            ("English", "model"),
            ("Hindi", "model-hi")
        ]
        
        for lang, model_path in models_to_test:
            if os.path.exists(model_path):
                try:
                    model = vosk.Model(model_path)
                    print(f"✅ {lang} model loaded successfully from {model_path}")
                except Exception as e:
                    print(f"❌ Error loading {lang} model from {model_path}: {e}")
            else:
                print(f"⚠️  {lang} model directory not found: {model_path}")
        
        return True
    except ImportError:
        print("❌ Vosk library not installed")
        print("Install with: pip install vosk")
        return False
    except Exception as e:
        print(f"❌ Error testing Vosk: {e}")
        return False

def test_microphone_access():
    """Test actual microphone recording"""
    try:
        import sounddevice as sd
        import numpy as np
        
        print("\n🎙️  Testing microphone access...")
        print("Recording 3 seconds of audio...")
        
        duration = 3  # seconds
        sample_rate = 16000
        
        # Record audio
        audio_data = sd.rec(int(duration * sample_rate), 
                           samplerate=sample_rate, 
                           channels=1, 
                           dtype='float64')
        sd.wait()  # Wait until recording is finished
        
        # Check if we got actual audio data
        max_amplitude = np.max(np.abs(audio_data))
        
        if max_amplitude > 0.001:  # Some reasonable threshold
            print(f"✅ Microphone working! Max amplitude: {max_amplitude:.4f}")
            print("💡 Try speaking during the test for better results")
            return True
        else:
            print(f"⚠️  Microphone might not be working. Max amplitude: {max_amplitude:.4f}")
            print("💡 Make sure your microphone is not muted and try speaking during the test")
            return False
            
    except Exception as e:
        print(f"❌ Error testing microphone: {e}")
        return False

def main():
    print("🔧 WhisperBoard Audio Diagnostic Tool")
    print("=" * 50)
    
    # Test all components
    sounddevice_ok = test_sounddevice()
    vosk_ok = test_vosk()
    
    if sounddevice_ok:
        mic_ok = test_microphone_access()
    else:
        mic_ok = False
    
    print("\n📊 Diagnosis Summary:")
    print("-" * 30)
    print(f"SoundDevice: {'✅ OK' if sounddevice_ok else '❌ FAIL'}")
    print(f"Vosk Models: {'✅ OK' if vosk_ok else '❌ FAIL'}")
    print(f"Microphone:  {'✅ OK' if mic_ok else '❌ FAIL'}")
    
    if all([sounddevice_ok, vosk_ok, mic_ok]):
        print("\n🎉 All tests passed! WhisperBoard should work with real microphone input.")
        print("Run: streamlit run app.py")
    else:
        print("\n🔧 Issues detected. Please address the failed components above.")
        
        if not sounddevice_ok:
            print("💡 Install system audio libraries:")
            print("   Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio")
            print("   macOS: brew install portaudio")
            print("   Then: pip install sounddevice")
        
        if not vosk_ok:
            print("💡 Download Vosk models:")
            print("   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
            print("   unzip vosk-model-en-us-0.22.zip && mv vosk-model-en-us-0.22 model")

if __name__ == "__main__":
    main()