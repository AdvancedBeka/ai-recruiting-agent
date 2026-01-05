"""
Простой тест Gemini API - проверяем базовую связь
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n" + "=" * 60)
print("Простой тест Gemini API")
print("=" * 60)

# Проверяем зависимости
try:
    import google.generativeai as genai
    print("✓ google-generativeai установлен")
except ImportError:
    print("✗ google-generativeai не установлен")
    print("  Запустите: pip install google-generativeai")
    sys.exit(1)

# Загружаем конфиг
from config import Settings
settings = Settings()

if not settings.google_api_key:
    print("\n✗ GOOGLE_API_KEY не настроен в .env")
    print("\nЧтобы получить API ключ:")
    print("1. Перейдите: https://aistudio.google.com/app/apikey")
    print("2. Создайте новый API ключ")
    print("3. Добавьте в .env файл:")
    print("   GOOGLE_API_KEY=ваш-ключ-здесь")
    sys.exit(1)

print(f"✓ API ключ найден: {settings.google_api_key[:10]}...")

# Настраиваем API
print("\n" + "=" * 60)
print("Инициализация Gemini API")
print("=" * 60)

try:
    genai.configure(api_key=settings.google_api_key)
    print("✓ API настроен")
except Exception as e:
    print(f"✗ Ошибка настройки API: {e}")
    sys.exit(1)

# Тест 1: Простой вопрос
print("\n" + "=" * 60)
print("Тест 1: Простой вопрос")
print("=" * 60)

try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    print("✓ Модель загружена: gemini-2.5-pro")

    prompt = "Привет! Скажи 'Привет' в ответ одним словом."
    print(f"\nОтправляю: '{prompt}'")

    response = model.generate_content(prompt)

    print(f"✓ Получен ответ!")
    print(f"\nОтвет Gemini: {response.text}")

except Exception as e:
    print(f"\n✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()

# Тест 2: Простая математика
print("\n" + "=" * 60)
print("Тест 2: Математика")
print("=" * 60)

try:
    prompt = "Сколько будет 2+2? Ответь только числом."
    print(f"\nОтправляю: '{prompt}'")

    response = model.generate_content(prompt)

    print(f"✓ Получен ответ!")
    print(f"\nОтвет Gemini: {response.text}")

except Exception as e:
    print(f"\n✗ Ошибка: {e}")

# Тест 3: JSON формат
print("\n" + "=" * 60)
print("Тест 3: Ответ в JSON формате")
print("=" * 60)

try:
    prompt = """
Ответь в формате JSON со следующими полями:
{
  "status": "ok",
  "message": "Тест пройден"
}

Ответь ТОЛЬКО JSON, без дополнительного текста.
"""
    print(f"\nОтправляю запрос на JSON...")

    response = model.generate_content(prompt)

    print(f"✓ Получен ответ!")
    print(f"\nОтвет Gemini:")
    print(response.text)

    # Пробуем распарсить JSON
    import json
    text = response.text.strip()
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    text = text.strip()

    data = json.loads(text)
    print(f"\n✓ JSON успешно распарсен:")
    print(f"  status: {data.get('status')}")
    print(f"  message: {data.get('message')}")

except json.JSONDecodeError as e:
    print(f"\n⚠ Не удалось распарсить JSON: {e}")
    print(f"Сырой ответ: {response.text}")
except Exception as e:
    print(f"\n✗ Ошибка: {e}")

# Тест 4: С параметрами generation
print("\n" + "=" * 60)
print("Тест 4: С настройками генерации")
print("=" * 60)

try:
    generation_config = {
        "temperature": 0.1,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 100,
    }

    prompt = "Опиши Python в двух предложениях."
    print(f"\nОтправляю с temperature=0.1...")

    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )

    print(f"✓ Получен ответ!")
    print(f"\nОтвет Gemini: {response.text}")

except Exception as e:
    print(f"\n✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()

# Итоги
print("\n" + "=" * 60)
print("Результаты тестирования")
print("=" * 60)

print("\n✅ Если все тесты прошли успешно, то:")
print("  • Gemini API работает")
print("  • Ваш API ключ валиден")
print("  • Можно использовать для matching")

print("\n⚠ Если были ошибки 429 (quota exceeded):")
print("  • Вы исчерпали дневной лимит")
print("  • Квоты обновятся завтра")
print("  • Используйте Sentence-BERT matcher (он работает отлично!)")

print("\n💡 Для matching резюме используйте:")
print("  python test_gemini.py")

print()
