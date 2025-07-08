#!/usr/bin/env python3
"""
Enhanced Text-to-Speech server with soft female voice
Improved Russian voice quality with softer, more pleasant tone
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
import scipy.signal

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load VITS model for Russian
print("Loading enhanced VITS Russian model for soft female voice...")
model_name = "facebook/mms-tts-rus"  # High-quality Russian TTS model
tokenizer = VitsTokenizer.from_pretrained(model_name)
model = VitsModel.from_pretrained(model_name)

if torch.cuda.is_available():
    model = model.cuda()
    print("Using CUDA for TTS acceleration")
else:
    print("Using CPU for TTS")

print("Enhanced VITS Russian TTS model loaded successfully")

def preprocess_russian_text(text):
    """Enhanced preprocessing for more natural Russian speech"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Add pauses for better speech flow
    text = text.replace(',', ', ')
    text = text.replace('.', '. ')
    text = text.replace('!', '! ')
    text = text.replace('?', '? ')
    
    # Expand common abbreviations
    text = text.replace('т.д.', 'так далее')
    text = text.replace('т.п.', 'тому подобное')
    text = text.replace('и т.д.', 'и так далее')
    text = text.replace('т.е.', 'то есть')
    text = text.replace('др.', 'другой')
    text = text.replace('г.', 'год')
    
    # Handle numbers (basic)
    text = re.sub(r'\b(\d+)\b', lambda m: convert_number_to_words(int(m.group())), text)
    
    return text

def convert_number_to_words(num):
    """Convert numbers to Russian words"""
    numbers = {
        0: "ноль", 1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
        6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять",
        11: "одиннадцать", 12: "двенадцать", 13: "тринадцать", 14: "четырнадцать", 15: "пятнадцать",
        16: "шестнадцать", 17: "семнадцать", 18: "восемнадцать", 19: "девятнадцать", 20: "двадцать"
    }
    return numbers.get(num, str(num))

def enhance_voice_quality(audio, sample_rate=22050):
    """Apply audio processing to create softer, more pleasant female voice"""
    # Convert to float for processing
    audio = audio.astype(np.float32)
    
    # Apply pitch shift to make voice slightly higher (more feminine)
    # Simple pitch shifting by resampling
    pitch_factor = 1.08  # Slightly higher pitch
    new_length = int(len(audio) / pitch_factor)
    audio_pitched = scipy.signal.resample(audio, new_length)
    
    # Apply gentle low-pass filter to soften harsh frequencies
    nyquist = sample_rate / 2
    cutoff = 8000  # Cut frequencies above 8kHz for softer sound
    sos = scipy.signal.butter(6, cutoff / nyquist, btype='low', output='sos')
    audio_filtered = scipy.signal.sosfilt(sos, audio_pitched)
    
    # Apply gentle compression to even out volume levels
    # Simple soft compression
    threshold = 0.6
    ratio = 4.0
    compressed = np.where(
        np.abs(audio_filtered) > threshold,
        np.sign(audio_filtered) * (threshold + (np.abs(audio_filtered) - threshold) / ratio),
        audio_filtered
    )
    
    # Apply gentle reverb effect for warmth
    # Simple reverb with short delay
    delay_samples = int(0.02 * sample_rate)  # 20ms delay
    reverb = np.copy(compressed)
    if len(reverb) > delay_samples:
        reverb[delay_samples:] += compressed[:-delay_samples] * 0.15
    
    # Normalize and apply gentle saturation
    reverb = reverb / np.max(np.abs(reverb)) * 0.95
    
    # Apply soft saturation for warmth
    reverb = np.tanh(reverb * 1.2) * 0.8
    
    return reverb

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
        print(f"Synthesizing soft Russian female voice: {text}")
        
        # Tokenize text
        inputs = tokenizer(text, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate speech with enhanced parameters for female voice
        with torch.no_grad():
            # Use temperature for more expressive speech
            waveform = model(**inputs).waveform
        
        # Convert to numpy and ensure proper shape
        audio = waveform.cpu().numpy().squeeze()
        
        # Ensure audio is mono and properly shaped
        if len(audio.shape) > 1:
            audio = audio[0]  # Take first channel if stereo
        
        # Apply voice enhancement for soft female voice
        audio = enhance_voice_quality(audio, 22050)
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio)) * 0.9
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            # Save as WAV file with proper sample rate
            sf.write(tmp_file.name, audio, 22050)
            
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
        'model': 'vits-russian-soft-female',
        'language': 'ru'
    })

if __name__ == '__main__':
    print("Starting enhanced Russian TTS server with soft female voice on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
