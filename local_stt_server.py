#!/usr/bin/env python3
"""
Local Speech-to-Text server using OpenAI Whisper
Mimics the OpenAI API format for drop-in replacement
"""

from flask import Flask, request, jsonify
import whisper
import tempfile
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Get model from environment or default to base
stt_model = os.getenv('STT_MODEL', 'whisper-medium').replace('whisper-', '')
print(f"Loading Whisper {stt_model} model for Russian recognition...")
model = whisper.load_model(stt_model)
print(f"Whisper {stt_model} model loaded successfully")

@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcribe():
    try:
        # Check if audio file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['file']
        
        # Get language preference from form data or default to auto-detect
        language = request.form.get('language', None)
        
        # Map common language codes
        language_map = {
            'en': 'english',
            'ru': 'russian', 
            'uk': 'ukrainian',
            'auto': None
        }
        
        if language in language_map:
            language = language_map[language]
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            
            # Optimized Russian transcription with Whisper Large
            result = model.transcribe(
                tmp_file.name,
                language="russian",
                task="transcribe",
                initial_prompt="Говорящий произносит русские слова четко и ясно. Часто используемые слова: Голова, Головастик, Чатбот, как дела, привет, спасибо, помоги, расскажи, что делаешь.",
                word_timestamps=True,
                condition_on_previous_text=False,
                temperature=0.0,  # Most deterministic
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6
            )
            
            # Clean up temp file
            os.unlink(tmp_file.name)
            
            # Return in OpenAI API format with detected language
            return jsonify({
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown')
            })
            
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'service': 'STT',
        'model': stt_model,
        'language': 'ru'
    })

if __name__ == '__main__':
    print("Starting local Whisper STT server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
