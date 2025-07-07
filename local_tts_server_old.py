#!/usr/bin/env python3
"""
Local Text-to-Speech server using SpeechT5
Optimized for Russian language
Mimics the OpenAI API format for drop-in replacement
"""

from flask import Flask, request, jsonify, send_file
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import soundfile as sf
import tempfile
import os
import logging
import re

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

print("Loading SpeechT5 models for Russian...")
# Load SpeechT5 model and processor
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# Load speaker embeddings - use a speaker with clearer voice for Russian
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[0]["xvector"]).unsqueeze(0)  # Changed speaker

print("SpeechT5 models loaded successfully (Russian optimized)")

def preprocess_russian_text(text):
    """Preprocess Russian text for better TTS pronunciation"""
    # Remove extra punctuation that might confuse TTS
    text = re.sub(r'[^\w\s\.,!?;:-]', '', text)
    
    # Add pauses after punctuation for more natural speech
    text = re.sub(r'([.!?])\s*', r'\1 ', text)
    text = re.sub(r'([,;:])\s*', r'\1 ', text)
    
    # Ensure proper spacing
    text = re.sub(r'\s+', ' ', text).strip()
    
    # If text is too long, truncate it
    if len(text) > 500:
        text = text[:500] + "..."
    
    return text

@app.route('/v1/audio/speech', methods=['POST'])
@app.route('/synthesize', methods=['POST'])  # Support both endpoints
def text_to_speech():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Support both 'input' (OpenAI format) and 'text' (SpeechT5 format)
        text = data.get('input') or data.get('text')
        if not text:
            return jsonify({'error': 'No text input provided'}), 400
        
        # Preprocess Russian text for better pronunciation
        text = preprocess_russian_text(text)
        print(f"Synthesizing Russian text: {text}")
        
        # Process text
        inputs = processor(text=text, return_tensors="pt")
        
        # Generate speech for Russian text
        with torch.no_grad():
            speech = model.generate_speech(
                inputs["input_ids"], 
                speaker_embeddings, 
                vocoder=vocoder
            )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            sf.write(tmp_file.name, speech.numpy(), samplerate=16000)
            
            # Return audio file
            return send_file(tmp_file.name, 
                           mimetype='audio/wav',
                           as_attachment=True,
                           download_name='russian_speech.wav')
            
    except Exception as e:
        logging.error(f"Russian TTS error: {e}")
        print(f"TTS Error details: {e}")  # Debug print
        return jsonify({'error': f'TTS processing failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': 'speecht5-russian', 'language': 'ru'})

if __name__ == '__main__':
    print("Starting local Russian TTS server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
