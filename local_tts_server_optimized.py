#!/usr/bin/env python3
"""
Local Text-to-Speech server using SpeechT5
Optimized for Russian language with GPU memory management
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
import gc
from contextlib import contextmanager

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GPU Memory optimization settings
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

# Set conservative memory allocation
if torch.cuda.is_available():
    torch.cuda.memory.set_per_process_memory_fraction(0.6)  # Use only 60% of GPU memory
    torch.cuda.empty_cache()

print("Loading SpeechT5 models for Russian with memory optimization...")

# Load models with memory optimization
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")

# Load models on CPU first, then move to GPU
with torch.no_grad():
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# Load speaker embeddings
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[0]["xvector"]).unsqueeze(0)

# Move to GPU with memory management
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

if device.type == "cuda":
    torch.cuda.empty_cache()
    
    # Enable memory efficient operations
    try:
        torch.backends.cuda.enable_flash_sdp(True)
    except:
        pass

model = model.to(device)
vocoder = vocoder.to(device)
speaker_embeddings = speaker_embeddings.to(device)

# Force cleanup
gc.collect()
if device.type == "cuda":
    torch.cuda.empty_cache()
    print(f"GPU memory allocated after loading: {torch.cuda.memory_allocated()/1024**3:.2f} GB")

print("SpeechT5 models loaded successfully with memory optimization")

@contextmanager
def gpu_memory_manager():
    """Context manager for GPU memory cleanup"""
    try:
        yield
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

def preprocess_russian_text(text):
    """Preprocess Russian text for better TTS pronunciation"""
    # Remove extra punctuation that might confuse TTS
    text = re.sub(r'[^\w\s\.,!?;:-]', '', text)
    
    # Add pauses after punctuation for more natural speech
    text = re.sub(r'([.!?])\s*', r'\1 ', text)
    text = re.sub(r'([,;:])\s*', r'\1 ', text)
    
    # Ensure text is not too long (split long texts)
    max_length = 500
    if len(text) > max_length:
        # Split at sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        text = '. '.join(sentences[:3])  # Take first 3 sentences
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0]  # Cut at word boundary
    
    return text

def generate_speech(text):
    """Generate speech with memory management"""
    with gpu_memory_manager():
        try:
            # Preprocess text
            text = preprocess_russian_text(text)
            logger.info(f"Generating speech for: {text[:50]}...")
            
            # Process inputs
            inputs = processor(text=text, return_tensors="pt")
            
            # Move inputs to device
            input_ids = inputs["input_ids"].to(device)
            
            # Generate speech with memory optimization
            with torch.no_grad():
                speech = model.generate_speech(input_ids, speaker_embeddings, vocoder=vocoder)
            
            # Convert to numpy and clean up GPU tensors immediately
            speech_np = speech.cpu().numpy()
            
            # Clean up intermediate tensors
            del input_ids, speech
            
            logger.info("Speech generated successfully")
            return speech_np
            
        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"CUDA OOM Error: {e}")
            # Emergency cleanup
            torch.cuda.empty_cache()
            gc.collect()
            raise Exception("GPU memory exhausted. Try shorter text or restart the service.")
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "TTS"})

@app.route('/v1/audio/speech', methods=['POST'])
def synthesize_openai_format():
    """OpenAI-compatible endpoint"""
    try:
        data = request.get_json()
        text = data.get('input', '')
        
        if not text:
            return jsonify({"error": "No input text provided"}), 400
        
        # Generate speech
        speech = generate_speech(text)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            sf.write(temp_file.name, speech, 16000)
            temp_filename = temp_file.name
        
        # Return the audio file
        return send_file(temp_filename, as_attachment=True, download_name='speech.wav', mimetype='audio/wav')
        
    except Exception as e:
        logger.error(f"Error in OpenAI format synthesis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Custom synthesis endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Generate speech
        speech = generate_speech(text)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            sf.write(temp_file.name, speech, 16000)
            temp_filename = temp_file.name
        
        # Return the audio file
        return send_file(temp_filename, as_attachment=True, download_name='speech.wav', mimetype='audio/wav')
        
    except Exception as e:
        logger.error(f"Error in synthesis: {e}")
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
            }
        })
    else:
        return jsonify({"gpu_memory": "CUDA not available"})

if __name__ == '__main__':
    print("Starting optimized TTS server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
