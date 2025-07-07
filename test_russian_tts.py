#!/usr/bin/env python3
"""
Тест локального русского TTS сервера
"""

import requests
import os

def test_russian_tts():
    """Тестирование русского TTS"""
    print("🇷🇺 Тест русского TTS сервера...")
    
    test_phrases = [
        "Привет! Меня зовут Сота.",
        "Как дела? Что нового?",
        "Сегодня хорошая погода.",
        "Я понимаю русский язык.",
        "Спасибо за ваш вопрос!"
    ]
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n{i}. Синтез: '{phrase}'")
        
        try:
            # Тест OpenAI-style endpoint
            response = requests.post('http://localhost:5000/v1/audio/speech', 
                                   json={'input': phrase},
                                   timeout=30)
            
            if response.status_code == 200:
                filename = f'test_russian_{i}.wav'
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   ✅ Успешно: {filename}")
                
                # Check file size
                size = os.path.getsize(filename)
                print(f"   📊 Размер: {size} байт")
                
                # Clean up
                os.remove(filename)
            else:
                print(f"   ❌ Ошибка {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Исключение: {e}")

def test_health():
    """Тест состояния TTS сервера"""
    print("\n🏥 Проверка состояния TTS сервера...")
    
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Статус: {result.get('status')}")
            print(f"   🤖 Модель: {result.get('model')}")
            print(f"   🌐 Язык: {result.get('language')}")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Недоступен: {e}")

if __name__ == "__main__":
    print("🎙️ Тестирование русского TTS сервера")
    print("=" * 40)
    
    test_health()
    test_russian_tts()
    
    print("\n✅ Тестирование завершено!")
    print("\n💡 Теперь TTS оптимизирован для русского языка:")
