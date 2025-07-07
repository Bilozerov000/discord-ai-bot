#!/usr/bin/env python3
"""
Тест локального STT сервера с русским языком
"""

import requests
import tempfile
import os
from gtts import gTTS

def test_russian_phrases():
    """Тестирование различных русских фраз"""
    
    test_phrases = [
        "Голова, как дела?",
        "Головастик, расскажи анекдот",
        "Чатбот, какая сегодня погода?",
        "Привет, меня зовут Олексий",
        "Как установить программное обеспечение?",
        "Расскажи мне о машинном обучении",
        "Что ты умеешь делать?",
        "Спасибо за помощь"
    ]
    
    print("🧪 Тестирование русского распознавания речи...")
    print("=" * 50)
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n{i}. Тест фразы: '{phrase}'")
        
        try:
            # Создаем аудио файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_audio:
                tts = gTTS(text=phrase, lang='ru')
                tts.save(tmp_audio.name)
                
                # Тестируем распознавание
                with open(tmp_audio.name, 'rb') as audio_file:
                    files = {'file': audio_file}
                    data = {'language': 'ru'}
                    
                    response = requests.post('http://localhost:5001/v1/audio/transcriptions', 
                                           files=files, data=data)
                
                # Удаляем временный файл
                os.unlink(tmp_audio.name)
                
                if response.status_code == 200:
                    result = response.json()
                    detected_text = result['text'].strip()
                    language = result.get('language', 'unknown')
                    
                    print(f"   ✅ Распознано: '{detected_text}'")
                    print(f"   🔤 Язык: {language}")
                    
                    # Проверяем качество распознавания
                    similarity = calculate_similarity(phrase.lower(), detected_text.lower())
                    print(f"   📊 Схожесть: {similarity:.1f}%")
                    
                else:
                    print(f"   ❌ Ошибка: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Исключение: {e}")

def calculate_similarity(original, detected):
    """Простое вычисление схожести строк"""
    if not original or not detected:
        return 0.0
    
    # Убираем знаки препинания и лишние пробелы
    import re
    original = re.sub(r'[^\w\s]', '', original).strip()
    detected = re.sub(r'[^\w\s]', '', detected).strip()
    
    # Простая проверка на совпадающие слова
    orig_words = set(original.split())
    det_words = set(detected.split())
    
    if not orig_words:
        return 0.0
        
    common_words = orig_words.intersection(det_words)
    return (len(common_words) / len(orig_words)) * 100

def test_bot_triggers():
    """Тестирование триггерных слов бота"""
    print("\n🎯 Тестирование триггерных слов...")
    print("=" * 50)
    
    triggers = ["Голова", "Головастик", "Чатбот"]
    
    for trigger in triggers:
        phrase = f"{trigger}, привет!"
        print(f"\nТест триггера: '{phrase}'")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_audio:
                tts = gTTS(text=phrase, lang='ru')
                tts.save(tmp_audio.name)
                
                with open(tmp_audio.name, 'rb') as audio_file:
                    files = {'file': audio_file}
                    data = {'language': 'ru'}
                    
                    response = requests.post('http://localhost:5001/v1/audio/transcriptions', 
                                           files=files, data=data)
                
                os.unlink(tmp_audio.name)
                
                if response.status_code == 200:
                    result = response.json()
                    detected = result['text'].strip()
                    print(f"   ✅ Распознано: '{detected}'")
                    
                    # Проверяем, есть ли триггерное слово в результате
                    if trigger.lower() in detected.lower():
                        print(f"   🎯 Триггер '{trigger}' успешно распознан!")
                    else:
                        print(f"   ⚠️  Триггер '{trigger}' не найден в результате")
                else:
                    print(f"   ❌ Ошибка: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Исключение: {e}")

if __name__ == "__main__":
    print("🇷🇺 Тестирование русской локализации Discord бота")
    print("=" * 60)
    
    # Проверяем доступность сервиса
    try:
        response = requests.get('http://localhost:5001/health', timeout=5)
        if response.status_code == 200:
            print("✅ STT сервер доступен")
        else:
            print("❌ STT сервер недоступен")
            exit(1)
    except:
        print("❌ Не удается подключиться к STT серверу")
        exit(1)
    
    # Запускаем тесты
    test_russian_phrases()
    test_bot_triggers()
    
    print("\n🎉 Тестирование завершено!")
    print("\n💡 Советы:")
    print("- Используйте триггеры: 'Голова', 'Головастик', 'Чатбот'")
    print("- Говорите четко и не слишком быстро")
    print("- Бот теперь оптимизирован для русского языка")
