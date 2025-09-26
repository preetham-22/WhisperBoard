#!/usr/bin/env python3
"""
Generate a test WAV file for WhisperBoard file upload testing
Creates a simple sine wave audio file with the correct format
"""

import wave
import numpy as np

def create_test_wav_file(filename="test_speech_16k.wav", duration=3, frequency=440):
    """
    Create a test WAV file with the correct format for WhisperBoard
    
    Args:
        filename: Output filename
        duration: Duration in seconds
        frequency: Tone frequency in Hz
    """
    # Audio parameters for Vosk compatibility
    sample_rate = 16000  # 16kHz (required by Vosk)
    channels = 1         # Mono
    sampwidth = 2        # 16-bit
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Create a simple sine wave that fades in and out
    wave_data = np.sin(frequency * 2 * np.pi * t)
    
    # Add fade in/out to make it more natural
    fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
    
    # Fade in
    if len(wave_data) > fade_samples:
        fade_in = np.linspace(0, 1, fade_samples)
        wave_data[:fade_samples] *= fade_in
    
    # Fade out
    if len(wave_data) > fade_samples:
        fade_out = np.linspace(1, 0, fade_samples)
        wave_data[-fade_samples:] *= fade_out
    
    # Convert to 16-bit integers
    wave_data = (wave_data * 32767).astype(np.int16)
    
    # Write WAV file
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print(f"✅ Created test WAV file: {filename}")
    print(f"   • Duration: {duration} seconds")
    print(f"   • Sample Rate: {sample_rate} Hz")
    print(f"   • Channels: {channels} (mono)")
    print(f"   • Bit Depth: {sampwidth * 8}-bit")
    print(f"   • File Size: {len(wave_data) * sampwidth} bytes")
    print(f"   • Frequency: {frequency} Hz")

if __name__ == "__main__":
    print("🎵 WhisperBoard Test WAV File Generator")
    print("=" * 50)
    
    # Create a test file
    create_test_wav_file("test_audio.wav", duration=3, frequency=440)
    
    print(f"\n📁 You can now upload 'test_audio.wav' to test the file upload feature!")
    print(f"   Note: This is just a tone - for real speech recognition,")
    print(f"   you'll need a WAV file with actual speech content.")