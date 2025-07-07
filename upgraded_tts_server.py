#!/usr/bin/env python3
"""
Upgraded Text-to-Speech server using VITS models
Much better Russian voice quality than SpeechT5
"""

from flask import Flask, request, jsonify, send_file
import torch
from transformers import VitsModel, VitsTokenizer
import numpy as np
import tempfile
import io
import soundfile as sf
import logging
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load VITS model for Russian
print("Loading VITS Russian model for high-quality speech synthesis...")
model_name = "facebook/mms-tts-rus"  # High-quality Russian TTS model
tokenizer = VitsTokenizer.from_pretrained(model_name)
model = VitsModel.from_pretrained(model_name)

if torch.cuda.is_available():
    model = model.cuda()
    print("Using CUDA for TTS acceleration")
else:
    print("Using CPU for TTS")

print("VITS Russian TTS model loaded successfully")

def preprocess_russian_text(text):
    """Preprocess Russian text for better synthesis"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Expand common abbreviations
    text = text.replace('т.д.', 'так далее')
    text = text.replace('т.п.', 'тому подобное')
    text = text.replace('и т.д.', 'и так далее')
    text = text.replace('т.е.', 'то есть')
    text = text.replace('др.', 'другой')
    
    # Handle numbers (basic)
    text = re.sub(r'\b(\d+)\b', lambda m: convert_number_to_words(int(m.group())), text)
    
    return text

def convert_number_to_words(num):
    """Convert numbers to Russian words (basic implementation)"""
    if num == 0: return "ноль"
    if num == 1: return "один"
    if num == 2: return "два"
    if num == 3: return "три"
    if num == 4: return "четыре"
    if num == 5: return "пять"
    if num == 6: return "шесть"
    if num == 7: return "семь"
    if num == 8: return "восемь"
    if num == 9: return "девять"
    if num == 10: return "десять"
    return str(num)  # Fallback for complex numbers

@app.route('/v1/audio/speech', methods=['POST'])
@app.route('/synthesize', methods=['POST'])
def synthesize():
    try:
        # Get JSON data
        if request.is_json:
            data = request.json
            text = data.get('input') or data.get('text')
        else:
            # Handle form data
            text = request.form.get('input') or request.form.get('text')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Preprocess text for better Russian synthesis
        text = preprocess_russian_text(text)
        print(f"Synthesizing Russian text: {text}")
        
        # Tokenize text
        inputs = tokenizer(text, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate speech
        with torch.no_grad():
            waveform = model(**inputs).waveform
        
        # Convert to numpy and ensure proper shape
        audio = waveform.cpu().numpy().squeeze()
        
        # Ensure audio is mono and properly shaped
        if len(audio.shape) > 1:
            audio = audio[0]  # Take first channel if stereo
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio))
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            # Save as WAV file with proper sample rate
            sf.write(tmp_file.name, audio, 22050)  # VITS typically uses 22kHz
            
            # Return the audio file
            return send_file(
                tmp_file.name, 
                mimetype='audio/wav',
                as_attachment=True,
                download_name='speech.wav'
            )
            
    except Exception as e:
        logging.error(f"TTS synthesis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'service': 'TTS',
        'model': 'vits-russian',
        'language': 'ru'
    })

if __name__ == '__main__':
    print("Starting upgraded Russian TTS server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
