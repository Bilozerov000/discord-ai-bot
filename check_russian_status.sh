#!/bin/bash
# Проверка статуса Discord бота на русском языке

echo "🤖 Статус Discord AI бота (Русская версия)"
echo "=========================================="

echo ""
echo "📊 Статус сервисов:"

# Проверка Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama (LLM): Работает на порту 11434"
else
    echo "❌ Ollama (LLM): Не отвечает"
fi

# Проверка STT
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ STT Сервер: Работает на порту 5001 (Русский язык)"
else
    echo "❌ STT Сервер: Не отвечает"
fi

# Проверка TTS
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ TTS Сервер: Работает на порту 5000" 
else
    echo "❌ TTS Сервер: Не отвечает"
fi

# Проверка Discord бота
if pgrep -f "node bot.js" > /dev/null; then
    echo "✅ Discord Бот: Работает (PID: $(pgrep -f 'node bot.js'))"
else
    echo "❌ Discord Бот: Не работает"
fi

echo ""
echo "🇷🇺 Настройки русского языка:"
echo "• Триггеры: Голова, Головастик, Чатбот"
echo "• STT язык: Русский (принудительно)"
echo "• Системные промпты: На русском языке"
echo "• TTS: Локальный SpeechT5"

echo ""
echo "💾 Использование ресурсов:"
echo "Память: $(free -h | awk 'NR==2{printf "%.1f/%.1fGB (%.1f%%)", $3/1024, $2/1024, $3*100/$2}')"

if command -v nvidia-smi &> /dev/null; then
    echo "GPU: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf "%.1f/%.1fGB", $1/1024, $2/1024}')"
fi

echo ""
echo "📋 Как протестировать:"
echo "1. Присоединитесь к голосовому каналу в Discord"
echo "2. Используйте команду /join чтобы пригласить бота"  
echo "3. Скажите одно из триггерных слов:"
echo "   • 'Голова, как дела?'"
echo "   • 'Головастик, расскажи анекдот'"
echo "   • 'Чатбот, какая погода?'"
echo "4. Бот ответит на русском языке"

echo ""
echo "🔧 Полезные команды:"
echo "- Просмотр логов бота: tail -f bot.log"
echo "- Тест русского языка: .venv/bin/python test_russian.py"
echo "- Остановка бота: pkill -f 'node bot.js'"  
echo "- Перезапуск: node bot.js > bot.log 2>&1 &"
