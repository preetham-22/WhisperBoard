#!/usr/bin/env python3
"""
Advanced Telugu model recognition test with real audio input
"""
import vosk
import sounddevice as sd
import queue
import json
import time
import threading
import sys

def test_live_recognition(model_path, language_name, duration=10):
    """Test live audio recognition for a specific model"""
    print(f"\n🎙️ Testing live recognition for {language_name}")
    print(f"Model path: {model_path}")
    print("="*60)
    
    try:
        # Load model
        model = vosk.Model(model_path)
        recognizer = vosk.KaldiRecognizer(model, 16000)
        recognizer.SetWords(True)
        
        print("✅ Model and recognizer loaded successfully")
        
        # Audio configuration
        audio_queue = queue.Queue()
        stop_flag = threading.Event()
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            audio_queue.put(bytes(indata))
        
        print(f"\n🔴 Starting {duration}-second recording test...")
        print(f"Please speak in {language_name} now!")
        print("-" * 60)
        
        # Start audio stream
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=4000,  # Smaller block size for more responsive recognition
            device=None,
            dtype='int16',
            channels=1,
            callback=audio_callback
        ):
            
            start_time = time.time()
            final_results = []
            partial_count = 0
            
            while time.time() - start_time < duration:
                try:
                    # Get audio data
                    data = audio_queue.get(timeout=0.1)
                    
                    # Process with recognizer
                    if recognizer.AcceptWaveform(data):
                        # Final result
                        result = json.loads(recognizer.Result())
                        if result.get('text', '').strip():
                            final_text = result['text'].strip()
                            final_results.append(final_text)
                            print(f"🎯 FINAL: {final_text}")
                    else:
                        # Partial result
                        partial_result = json.loads(recognizer.PartialResult())
                        if partial_result.get('partial', '').strip():
                            partial_text = partial_result['partial'].strip()
                            partial_count += 1
                            print(f"🔄 PARTIAL ({partial_count}): {partial_text}")
                            
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"❌ Error during recognition: {e}")
                    break
        
        print("-" * 60)
        print(f"⏹️ Recording finished for {language_name}")
        
        # Summary
        print(f"\n📊 RESULTS SUMMARY for {language_name}:")
        print(f"   • Final results: {len(final_results)}")
        print(f"   • Partial results: {partial_count}")
        
        if final_results:
            print(f"   • Combined text: {' '.join(final_results)}")
        else:
            print(f"   • ⚠️ NO FINAL TEXT RECOGNIZED")
            if partial_count > 0:
                print(f"   • ✅ But {partial_count} partial results detected (audio is being processed)")
            else:
                print(f"   • ❌ No partial results either (possible audio/model issue)")
        
        return len(final_results) > 0, partial_count > 0
        
    except Exception as e:
        print(f"❌ ERROR testing {language_name}: {str(e)}")
        return False, False

def main():
    print("🔍 ADVANCED TELUGU MODEL RECOGNITION TEST")
    print("=" * 70)
    
    # Test all models
    models_to_test = [
        ("English", "model-English"),
        ("Hindi", "model-Hindi"), 
        ("Telugu", "model-Telugu")
    ]
    
    results = {}
    
    for language, model_path in models_to_test:
        if input(f"\nTest {language} model? (y/n): ").lower().startswith('y'):
            has_final, has_partial = test_live_recognition(model_path, language, duration=8)
            results[language] = {
                'final': has_final,
                'partial': has_partial
            }
            
            # Brief pause between tests
            print("\nWaiting 2 seconds before next test...")
            time.sleep(2)
    
    # Final comparison
    print("\n" + "=" * 70)
    print("🏁 FINAL COMPARISON:")
    print("=" * 70)
    
    for language, result in results.items():
        final_status = "✅" if result['final'] else "❌"
        partial_status = "✅" if result['partial'] else "❌"
        print(f"{language:10} | Final: {final_status} | Partial: {partial_status}")
    
    # Specific recommendations for Telugu
    if 'Telugu' in results:
        telugu_result = results['Telugu']
        print(f"\n🎯 TELUGU MODEL ANALYSIS:")
        
        if not telugu_result['final'] and not telugu_result['partial']:
            print("❌ Telugu model not responding to audio input")
            print("   Possible issues:")
            print("   • Model may be corrupted or incomplete")
            print("   • Audio input not compatible with model")
            print("   • Model trained on different audio format")
            
        elif not telugu_result['final'] and telugu_result['partial']:
            print("⚠️ Telugu model processes audio but doesn't finalize results")
            print("   Possible solutions:")
            print("   • Speak louder or closer to microphone")
            print("   • Try longer pauses between words") 
            print("   • Check if model expects specific Telugu dialect")
            print("   • Reduce background noise")
            
        else:
            print("✅ Telugu model working correctly!")

if __name__ == "__main__":
    main()