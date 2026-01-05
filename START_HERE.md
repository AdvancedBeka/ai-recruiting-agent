# 🚀 START HERE - AI Recruiting Agent

## Добро пожаловать!

Это **AI Recruiting Agent** - система для автоматизации рекрутинга с использованием AI.

---

## ⚡ Быстрый старт (5 минут)

### Шаг 1: Установка

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Шаг 2: Настройка

```bash
copy .env.example .env
notepad .env
```

Заполните в `.env`:
```env
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
```

**Для Gmail:** Получите App Password здесь: https://myaccount.google.com/security

### Шаг 3: Запуск

```bash
python test_email.py
```

Готово! Система автоматически получит резюме из вашей почты.

---

## 📚 Что дальше?

### Документация

| Файл | Для чего |
|------|----------|
| [README.md](README.md) | Общий обзор проекта |
| [QUICKSTART.md](QUICKSTART.md) | Подробная инструкция по запуску |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Полная сводка проекта |
| [ROADMAP.md](ROADMAP.md) | План развития (8 фаз) |

### Примеры кода

- [test_email.py](test_email.py) - Основной тест
- [examples/email_integration_demo.py](examples/email_integration_demo.py) - 6 примеров использования

---

## ✨ Что уже работает

✅ **Email Integration (100% готово)**
- Автоматическое получение резюме из email
- Поддержка Gmail, Yandex, Mail.ru, Outlook
- Сохранение вложений (PDF, DOCX, DOC, TXT, RTF)
- Защита от дубликатов
- Детальная статистика

---

## 🎯 Что планируется

🚧 **Resume Parsing** - Извлечение данных из резюме

📋 **Job Processing** - Управление вакансиями

🎯 **Matching Engine** - AI сопоставление (3 подхода):
- Semantic (Sentence-BERT)
- TF-IDF + ML
- LLM (GPT)

🌐 **REST API** - FastAPI backend

🎨 **Web UI** - Streamlit интерфейс

🐳 **Docker** - Контейнеризация

Подробно: [ROADMAP.md](ROADMAP.md)

---

## 💡 Примеры использования

### Получить непрочитанные письма

```python
from email_integration import EmailClient
from config import settings

with EmailClient(
    host=settings.email_host,
    port=settings.email_port,
    email_address=settings.email_address,
    password=settings.email_password
) as client:
    emails = client.fetch_unread_emails(limit=5)
    print(f"Found {len(emails)} emails")
```

### Сохранить резюме

```python
from email_integration import AttachmentHandler
from config import settings

handler = AttachmentHandler(
    storage_path=settings.resume_storage_path,
    processed_db_path=settings.processed_emails_db
)

# Обработать вложения
processed = handler.process_attachments(email_data)
print(f"Saved {len(processed)} resumes")

# Статистика
stats = handler.get_processed_stats()
print(f"Total: {stats['total_resumes_saved']} resumes")
```

---

## 🔧 Полезные команды

```bash
# Запустить тесты
python test_email.py

# Запустить примеры
python examples/email_integration_demo.py

# Показать статистику
python -c "from src.email_integration import AttachmentHandler; from src.config import settings; h = AttachmentHandler(settings.resume_storage_path, settings.processed_emails_db); print(h.get_processed_stats())"

# Очистить данные
rmdir /s /q data
```

---

## 🐛 Troubleshooting

### ❌ Authentication failed
→ Используйте **App Password**, не обычный пароль (для Gmail)

### ❌ No module named 'imapclient'
→ Запустите `pip install -r requirements.txt`

### ❌ Connection refused
→ Проверьте EMAIL_HOST и EMAIL_PORT в `.env`

### ⚠️ No unread emails found
→ Это нормально! Отправьте себе тестовое письмо с PDF/DOCX

Подробнее: [QUICKSTART.md](QUICKSTART.md) → секция Troubleshooting

---

## 📊 Структура проекта

```
testhome/
├── src/                      # Исходный код
│   ├── config.py            # Конфигурация
│   └── email_integration/   # Модуль работы с email
│       ├── email_client.py      # IMAP клиент
│       └── attachment_handler.py # Обработка вложений
│
├── examples/                 # Примеры использования
├── docs/                     # Документация
├── data/                     # Сохраненные резюме (создается автоматически)
│
├── test_email.py            # Главный тест
├── requirements.txt         # Зависимости
├── .env.example            # Пример конфигурации
│
└── README.md               # Документация
    QUICKSTART.md           # Быстрый старт
    PROJECT_SUMMARY.md      # Полная сводка
    ROADMAP.md             # План развития
```

---

## 📈 Прогресс

- ✅ **Phase 1:** Email Integration (DONE)
- 🚧 **Phase 2:** Resume Parsing (NEXT)
- 📅 **Phase 3-8:** Future development

**Текущий статус:** ~2300 строк кода, полностью рабочая email интеграция

---

## 🎓 Технологии

**Текущие:**
- Python 3.10+
- imapclient (IMAP)
- pydantic-settings (Config)

**Планируемые:**
- PyPDF2, python-docx (Parsing)
- sentence-transformers, openai (AI/ML)
- FastAPI (Backend)
- Streamlit (Frontend)
- Docker (Deploy)

---

## 📞 Нужна помощь?

1. **Быстрый старт:** [QUICKSTART.md](QUICKSTART.md)
2. **Детали проекта:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. **API документация:** [docs/email_integration.md](docs/email_integration.md)
4. **Архитектура:** [docs/architecture.md](docs/architecture.md)

---

## ✅ Следующие шаги

1. Запустите `python test_email.py` - проверьте email интеграцию
2. Изучите [examples/email_integration_demo.py](examples/email_integration_demo.py) - примеры использования
3. Прочитайте [ROADMAP.md](ROADMAP.md) - узнайте план развития
4. Начните работу над Phase 2 (Resume Parsing)

---

**Готово к работе!** 🎉

Начните с `python test_email.py`
