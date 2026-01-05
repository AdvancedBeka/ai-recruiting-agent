# Структура проекта AI Recruiting Agent

```
testhome/
│
├── 📄 README.md                    # Главная документация
├── 🚀 START_HERE.md                # Начните отсюда!
├── 📚 QUICKSTART.md                # Пошаговая инструкция
├── 📊 PROJECT_SUMMARY.md           # Полная сводка проекта
├── 🗺️  ROADMAP.md                  # План развития (8 фаз)
├── ✅ CHECKLIST.md                 # Checklist проекта
├── 🏗️  STRUCTURE.md                # Этот файл
│
├── ⚙️  requirements.txt            # Python зависимости
├── 🔧 .env.example                 # Пример конфигурации
├── 🚫 .gitignore                   # Git ignore правила
├── 🛠️  Makefile                    # Команды для разработки
│
├── 📁 src/                         # Исходный код
│   ├── __init__.py
│   ├── config.py                   # Конфигурация (Pydantic)
│   │
│   └── email_integration/          # Модуль интеграции с email
│       ├── __init__.py
│       ├── email_client.py         # IMAP клиент (450+ LOC)
│       └── attachment_handler.py   # Обработка вложений (350+ LOC)
│
├── 📁 examples/                    # Примеры использования
│   └── email_integration_demo.py   # 6 примеров
│
├── 📁 docs/                        # Документация
│   ├── architecture.md             # Архитектура системы
│   └── email_integration.md        # API документация
│
├── 📁 data/                        # Данные (создается автоматически)
│   ├── resumes/                    # Сохраненные резюме
│   │   └── YYYYMMDD_HHMMSS_ID_filename.pdf
│   └── processed_emails.json       # БД обработанных писем
│
├── 📁 tests/                       # Тесты (готова структура)
│   └── (будут добавлены в Phase 2)
│
├── 📁 venv/                        # Виртуальное окружение
│   └── (не коммитится в git)
│
└── 🧪 test_email.py                # Главный тестовый скрипт
```

## Описание компонентов

### 📄 Документация (корень)

| Файл | Размер | Назначение |
|------|--------|------------|
| README.md | ~4KB | Общий обзор, установка, использование |
| START_HERE.md | ~5KB | Быстрый старт для новичков |
| QUICKSTART.md | ~7KB | Подробная пошаговая инструкция |
| PROJECT_SUMMARY.md | ~12KB | Полная сводка проекта |
| ROADMAP.md | ~11KB | 8 фаз развития проекта |
| CHECKLIST.md | ~3KB | Checklist выполненных задач |
| STRUCTURE.md | ~2KB | Структура проекта (этот файл) |

### 🐍 Исходный код (src/)

#### config.py (~100 LOC)
- Pydantic Settings для конфигурации
- Автоматическое чтение .env
- Валидация параметров
- Создание директорий

#### email_integration/

**email_client.py** (~450 LOC)
- `EmailClient` класс
- IMAP подключение/отключение
- Получение писем (fetch_unread_emails)
- Парсинг MIME сообщений
- Декодирование вложений
- Context manager support
- Error handling и logging

**attachment_handler.py** (~350 LOC)
- `AttachmentHandler` класс
- Валидация форматов файлов
- Сохранение вложений
- SHA256 хеширование
- Отслеживание обработанных писем
- Статистика и отчеты

### 📚 Документация (docs/)

**architecture.md** (~400 LOC)
- Архитектура всей системы
- Диаграммы компонентов
- Технологический стек
- Паттерны проектирования
- План масштабирования

**email_integration.md** (~250 LOC)
- API документация модуля
- Примеры использования
- Структуры данных
- Настройка для разных провайдеров
- Troubleshooting

### 🧪 Тесты и примеры

**test_email.py** (~150 LOC)
- Тест подключения
- Получение и обработка писем
- Статистика
- Интеграционные тесты

**examples/email_integration_demo.py** (~250 LOC)
- Пример 1: Базовое подключение
- Пример 2: Получение писем
- Пример 3: Обработка вложений
- Пример 4: Context manager
- Пример 5: Статистика
- Пример 6: Фильтрация по subject

### 💾 Данные (data/)

**resumes/**
- Автоматически сохраненные резюме
- Формат имени: `YYYYMMDD_HHMMSS_EmailID_OriginalName.ext`
- Поддерживаемые форматы: .pdf, .docx, .doc, .txt, .rtf

**processed_emails.json**
```json
{
  "email_id": {
    "from": "candidate@example.com",
    "subject": "Application",
    "date": "...",
    "processed_date": "...",
    "attachments": [...]
  }
}
```

## Статистика

### Размер кодовой базы

```
Категория           Файлы    Строки    Размер
─────────────────────────────────────────────
Python код            4      ~900      ~35KB
Документация          7     ~1500      ~50KB
Примеры               2      ~400      ~15KB
Конфигурация          4       ~50       ~2KB
─────────────────────────────────────────────
ИТОГО                17     ~2850     ~102KB
```

### По языкам

- **Python:** ~900 строк
- **Markdown:** ~1500 строк
- **Config files:** ~50 строк

## Зависимости

### Production
```
imapclient==3.0.1      # IMAP клиент
email-validator==2.1.0 # Валидация email
pydantic==2.5.3        # Валидация данных
pydantic-settings==2.1.0 # Конфигурация
python-dotenv==1.0.0   # .env поддержка
```

### Development (планируется)
```
pytest                 # Тестирование
black                  # Форматирование
flake8                # Линтер
mypy                  # Type checking
```

## Следующая фаза структуры

### Phase 2: Resume Parsing

```
src/
├── resume_parser/
│   ├── __init__.py
│   ├── pdf_parser.py       # PDF парсинг
│   ├── docx_parser.py      # DOCX парсинг
│   ├── text_extractor.py   # Извлечение текста
│   └── ner_extractor.py    # NLP обработка
```

### Phase 3: Matching

```
src/
├── matching/
│   ├── __init__.py
│   ├── semantic_matcher.py    # Approach 1
│   ├── tfidf_matcher.py       # Approach 2
│   └── llm_matcher.py         # Approach 3
```

### Phase 4: API

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   ├── models/
│   └── services/
```

## Использование структуры

### Импорты

```python
# Конфигурация
from src.config import settings

# Email интеграция
from src.email_integration import EmailClient, AttachmentHandler

# Будущие модули (Phase 2+)
# from src.resume_parser import PDFParser
# from src.matching import SemanticMatcher
# from src.api import app
```

### Навигация

1. **Новичок?** → START_HERE.md
2. **Установка?** → QUICKSTART.md
3. **API?** → docs/email_integration.md
4. **Архитектура?** → docs/architecture.md
5. **План?** → ROADMAP.md
6. **Примеры?** → examples/

---

**Обновлено:** 30.12.2024
**Версия:** Phase 1 Complete
