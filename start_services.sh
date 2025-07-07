#!/bin/bash
# Start all local AI services for Discord bot

echo "Starting local AI services..."

# Start Ollama if not running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Start local STT server
echo "Starting local STT server..."
cd /home/oleksii/Documents/discord-ai-bot
.venv/bin/python local_stt_server.py &
STT_PID=$!

# Wait a moment for STT to start
sleep 5

# Start local TTS server
echo "Starting local TTS server..."
.venv/bin/python local_tts_server.py &
TTS_PID=$!

# Wait a moment for TTS to start
sleep 5

echo "All services started!"
echo "STT server: http://localhost:5001"
echo "TTS server: http://localhost:5000"
echo "LLM server: http://localhost:11434"
echo ""
echo "Process IDs:"
echo "STT PID: $STT_PID"
echo "TTS PID: $TTS_PID"
echo ""
echo "To stop services, run: ./stop_services.sh"
echo "To start Discord bot, run: node bot.js"
