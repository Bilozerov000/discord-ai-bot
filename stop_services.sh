#!/bin/bash
# Stop all local AI services

echo "Stopping local AI services..."

# Stop STT server
echo "Stopping STT server..."
pkill -f "local_stt_server.py"

# Stop TTS server
echo "Stopping TTS server..."
pkill -f "local_tts_server.py"

# Note: We're not stopping Ollama as it might be used by other applications
echo "Note: Ollama server left running (other apps might use it)"
echo "To stop Ollama manually: pkill -f 'ollama serve'"

echo "Local AI services stopped!"
