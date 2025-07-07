#!/usr/bin/env python3
"""
Test script for local STT server with multiple languages
"""

import requests
import tempfile
import os
from gtts import gTTS

def test_language(text, lang_code, lang_name):
    print(f"\n🧪 Testing {lang_name} recognition...")
    
    # Create audio file using gTTS
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_audio:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(tmp_audio.name)
        
        # Test transcription
        with open(tmp_audio.name, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {'language': 'auto'}  # Let it auto-detect
            
            response = requests.post('http://localhost:5001/v1/audio/transcriptions', 
                                   files=files, data=data)
            
        # Clean up
        os.unlink(tmp_audio.name)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Original: '{text}'")
            print(f"✅ Detected: '{result['text']}'")
            print(f"✅ Language: {result.get('language', 'unknown')}")
        else:
            print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    # Install gTTS if not available
    try:
        import gtts
    except ImportError:
        print("Installing gTTS for testing...")
        os.system("pip install gtts")
        import gtts
    
    print("🎯 Testing local STT server with multiple languages...")
    
    # Test different languages
    test_language("Hello, I am Sota, your Discord assistant", "en", "English")
    test_language("Привет, я Сота, ваш помощник в Discord", "ru", "Russian") 
    test_language("Привіт, я Сота, ваш помічник у Discord", "uk", "Ukrainian")
