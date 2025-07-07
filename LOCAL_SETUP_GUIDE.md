# Discord AI Bot - Local Setup Guide

## ✅ What's Now Running Locally

1. **LLM (Language Model)**: Llama 3.2 3B via Ollama (Port 11434)
2. **STT (Speech-to-Text)**: Local Whisper Base model (Port 5001) 
3. **TTS (Text-to-Speech)**: Local SpeechT5 model (Port 5000)

## 🚀 How to Start Everything

### Option 1: Manual Start (Recommended for testing)
```bash
# 1. Start STT server
nohup .venv/bin/python local_stt_server.py > stt.log 2>&1 &

# 2. Start TTS server  
nohup .venv/bin/python local_tts_server.py > tts.log 2>&1 &

# 3. Ollama should already be running, if not:
ollama serve &

# 4. Start Discord bot
node bot.js
```

### Option 2: Use Start Script
```bash
./start_services.sh
node bot.js
```

## 🧪 Testing Your Setup

### Test Ollama (LLM)
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:3b", "prompt": "Hello Sota!", "stream": false}'
```

### Test STT Server
```bash
curl http://localhost:5001/health
```

### Test TTS Server
```bash
curl http://localhost:5000/health
```

## 🛑 How to Stop Services
```bash
./stop_services.sh
```

## 📊 Resource Usage Estimates

- **Idle Power**: ~50-100W additional
- **During Voice Chat**: ~150-300W spikes
- **RAM Usage**: ~4-8GB
- **Disk Space**: ~8GB for all models

## 💰 Cost Comparison

**Before (Cloud APIs)**:
- GPT-4o-mini: ~$0.15 per 1M tokens
- Whisper: ~$0.006 per minute
- TTS: ~$0.015 per 1K characters

**After (Local)**:
- Electricity: ~$30-50/month (24/7 operation)
- Break-even: ~300-500 voice interactions per month

## 🔧 Configuration Files Updated

- `.env`: Updated endpoints and model names
- `local_stt_server.py`: Local Whisper API server
- `local_tts_server.py`: Local SpeechT5 API server
- `start_services.sh`: Convenience startup script
- `stop_services.sh`: Convenience stop script

## 🎯 Benefits Achieved

✅ **Zero API costs** for LLM, STT, and TTS  
✅ **Complete privacy** - no data leaves your machine  
✅ **No rate limits** - process as much as your hardware allows  
✅ **Offline capability** - works without internet  
✅ **Customizable** - can swap models easily  

## 🚨 Important Notes

1. Keep Ollama running in the background
2. TTS server takes ~30 seconds to start (downloading models)
3. STT quality is good with Whisper base, upgrade to "large" for better accuracy
4. Monitor system resources during heavy usage

## 🔄 Model Upgrades (Optional)

### Better STT (Higher accuracy, more resources)
```bash
# Edit local_stt_server.py, change:
model = whisper.load_model("large")  # instead of "base"
```

### Better LLM (More capable, needs more VRAM)
```bash
ollama pull llama3.1:8b  # or llama3.1:70b for even better quality
# Update .env: LLM=llama3.1:8b
```

Your Discord bot is now completely self-hosted! 🎉
