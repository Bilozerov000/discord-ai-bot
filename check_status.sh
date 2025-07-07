#!/bin/bash
# Discord Bot Status Check Script

echo "🤖 Discord AI Bot Status Check"
echo "================================"

echo ""
echo "📊 Service Status:"

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama (LLM): Running on port 11434"
else
    echo "❌ Ollama (LLM): Not responding"
fi

# Check STT
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ STT Server: Running on port 5001"
else
    echo "❌ STT Server: Not responding"
fi

# Check TTS
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ TTS Server: Running on port 5000" 
else
    echo "❌ TTS Server: Not responding"
fi

# Check Discord Bot
if pgrep -f "node bot.js" > /dev/null; then
    echo "✅ Discord Bot: Running (PID: $(pgrep -f 'node bot.js'))"
else
    echo "❌ Discord Bot: Not running"
fi

echo ""
echo "💾 Resource Usage:"
echo "Memory: $(free -h | awk 'NR==2{printf "%.1f/%.1fGB (%.1f%%)", $3/1024, $2/1024, $3*100/$2}')"

if command -v nvidia-smi &> /dev/null; then
    echo "GPU: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf "%.1f/%.1fGB", $1/1024, $2/1024}')"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Invite your bot to a Discord server"
echo "2. Join a voice channel"  
echo "3. Use /join command to bring bot to voice"
echo "4. Say 'Bot', 'Assistant', or 'Chatbot' to activate"
echo "5. Speak in English, Russian, or Ukrainian"

echo ""
echo "🔧 Useful Commands:"
echo "- Check bot logs: tail -f bot.log"
echo "- Stop bot: pkill -f 'node bot.js'"  
echo "- Restart bot: ./start_services.sh && node bot.js > bot.log 2>&1 &"
