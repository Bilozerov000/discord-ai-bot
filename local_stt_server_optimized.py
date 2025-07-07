#!/usr/bin/env python3
"""
Local Speech-to-Text server using Whisper
Optimized for Russian language with GPU memory management
Mimics the OpenAI API format for drop-in replacement
"""

from flask import Flask, request, jsonify
import whisper
import tempfile
import os
import logging
import torch
import gc
from contextlib import contextmanager

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GPU Memory optimization settings
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

# Set conservative memory allocation for STT
if torch.cuda.is_available():
    torch.cuda.memory.set_per_process_memory_fraction(0.4)  # Use only 40% for STT
    torch.cuda.empty_cache()

print("Loading Whisper model for Russian STT with memory optimization...")

# Use smaller model to save memory, but with better Russian support
try:
    # Try base model first (less memory intensive)
    model = whisper.load_model("base", device="cuda" if torch.cuda.is_available() else "cpu")
    model_name = "base"
    print(f"Loaded Whisper {model_name} model successfully")
except torch.cuda.OutOfMemoryError:
    print("CUDA OOM with base model, falling back to tiny...")
    torch.cuda.empty_cache()
    model = whisper.load_model("tiny", device="cuda" if torch.cuda.is_available() else "cpu")
    model_name = "tiny"
    print(f"Loaded Whisper {model_name} model successfully")

if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print(f"GPU memory allocated after loading: {torch.cuda.memory_allocated()/1024**3:.2f} GB")

@contextmanager
def gpu_memory_manager():
    """Context manager for GPU memory cleanup"""
    try:
        yield
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

def transcribe_audio(audio_path, language="ru"):
    """Transcribe audio with memory management"""
    with gpu_memory_manager():
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Transcribe with Russian language preference
            result = model.transcribe(
                audio_path, 
                language=language,
                fp16=torch.cuda.is_available(),  # Use fp16 for better memory efficiency
                verbose=False
            )
            
            text = result["text"].strip()
            logger.info(f"Transcription result: {text}")
            return text
            
        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"CUDA OOM Error during transcription: {e}")
            torch.cuda.empty_cache()
            gc.collect()
            raise Exception("GPU memory exhausted during transcription. Try shorter audio or restart the service.")
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "STT", 
        "model": model_name,
        "language": "ru"
    })

@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcribe():
    """OpenAI-compatible transcription endpoint"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['file']
        if audio_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get language from form data (default to Russian)
        language = request.form.get('language', 'ru')
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_filename = temp_file.name
        
        try:
            # Transcribe the audio
            text = transcribe_audio(temp_filename, language)
            
            # Return result in OpenAI format
            return jsonify({
                "text": text
            })
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    except Exception as e:
        logger.error(f"Error in transcription: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe_custom():
    """Custom transcription endpoint"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'ru')
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_filename = temp_file.name
        
        try:
            # Transcribe the audio
            text = transcribe_audio(temp_filename, language)
            
            return jsonify({
                "transcription": text,
                "language": language
            })
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    except Exception as e:
        logger.error(f"Error in custom transcription: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/memory_status', methods=['GET'])
def memory_status():
    """Check GPU memory status"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        return jsonify({
            "gpu_memory": {
                "allocated_gb": round(allocated, 2),
                "reserved_gb": round(reserved, 2),
                "total_gb": round(total, 2),
                "usage_percent": round((allocated / total) * 100, 1)
            },
            "model": model_name
        })
    else:
        return jsonify({"gpu_memory": "CUDA not available", "model": model_name})

if __name__ == '__main__':
    print(f"Starting optimized STT server with {model_name} model on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
