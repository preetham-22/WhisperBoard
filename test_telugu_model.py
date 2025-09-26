#!/usr/bin/env python3
"""
Debug script to test Telugu model loading and basic functionality
"""
import os
import vosk
import json
import sys

def test_model_loading(model_path):
    """Test if the model can be loaded successfully"""
    print(f"Testing model at: {model_path}")
    print(f"Model directory exists: {os.path.exists(model_path)}")
    
    if not os.path.exists(model_path):
        print("ERROR: Model directory not found!")
        return None
    
    # List contents of model directory
    print("\nModel directory contents:")
    for item in os.listdir(model_path):
        item_path = os.path.join(model_path, item)
        if os.path.isdir(item_path):
            print(f"  📁 {item}/")
            # List some contents of subdirectories
            sub_items = os.listdir(item_path)[:5]  # First 5 items
            for sub_item in sub_items:
                print(f"    📄 {sub_item}")
            if len(os.listdir(item_path)) > 5:
                print(f"    ... and {len(os.listdir(item_path)) - 5} more files")
        else:
            print(f"  📄 {item}")
    
    # Try to load the model
    print("\n" + "="*50)
    print("ATTEMPTING TO LOAD MODEL...")
    print("="*50)
    
    try:
        model = vosk.Model(model_path)
        print("✅ SUCCESS: Model loaded successfully!")
        return model
    except Exception as e:
        print(f"❌ ERROR: Failed to load model")
        print(f"Error details: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return None

def test_recognizer(model):
    """Test if recognizer can be created with the model"""
    if model is None:
        print("Cannot test recognizer - model is None")
        return None
    
    print("\n" + "="*50)
    print("TESTING RECOGNIZER CREATION...")
    print("="*50)
    
    try:
        recognizer = vosk.KaldiRecognizer(model, 16000)
        recognizer.SetWords(True)
        print("✅ SUCCESS: Recognizer created successfully!")
        
        # Test with some dummy data
        print("\nTesting with dummy audio data...")
        dummy_data = b'\x00' * 1600  # 0.1 second of silence at 16kHz
        
        # Test partial recognition
        partial_result = recognizer.PartialResult()
        print(f"Initial partial result: {partial_result}")
        
        # Test accepting waveform
        accepts = recognizer.AcceptWaveform(dummy_data)
        print(f"AcceptWaveform returned: {accepts}")
        
        if accepts:
            result = recognizer.Result()
            print(f"Final result: {result}")
        else:
            partial = recognizer.PartialResult()
            print(f"Partial result: {partial}")
        
        return recognizer
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create recognizer")
        print(f"Error details: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return None

def compare_models():
    """Compare Telugu model with working English model"""
    print("\n" + "="*50)
    print("COMPARING MODELS...")
    print("="*50)
    
    models_to_test = [
        ("English", "model-English"),
        ("Telugu", "model-Telugu"),
        ("Hindi", "model-Hindi")
    ]
    
    results = {}
    
    for name, path in models_to_test:
        print(f"\n--- Testing {name} Model ---")
        if os.path.exists(path):
            try:
                model = vosk.Model(path)
                results[name] = "✅ SUCCESS"
                print(f"{name}: Loaded successfully")
            except Exception as e:
                results[name] = f"❌ ERROR: {str(e)}"
                print(f"{name}: Failed to load - {str(e)}")
        else:
            results[name] = "❌ Directory not found"
            print(f"{name}: Directory not found")
    
    print(f"\n{'='*50}")
    print("COMPARISON SUMMARY:")
    print("="*50)
    for name, result in results.items():
        print(f"{name:10}: {result}")

if __name__ == "__main__":
    print("🔍 TELUGU MODEL DEBUGGING SCRIPT")
    print("=" * 60)
    
    # Test Telugu model specifically
    telugu_model = test_model_loading("model-Telugu")
    
    if telugu_model:
        test_recognizer(telugu_model)
    
    # Compare all models
    compare_models()
    
    print(f"\n{'='*60}")
    print("DEBUGGING COMPLETE")
    print("="*60)