# Быстрый старт - Email Integration

## Шаг 1: Установка зависимостей

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

## Шаг 2: Настройка конфигурации

1. Скопируйте файл конфигурации:
```bash
copy .env.example .env
```

2. Отредактируйте `.env` файл:

### Для Gmail:

```env
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
EMAIL_FOLDER=INBOX
```

**Как получить App Password для Gmail:**

1. Перейдите: https://myaccount.google.com/security
2. Включите **2-Step Verification**
3. Создайте **App Password** (Application-specific password)
4. Выберите "Mail" и ваше устройство
5. Скопируйте сгенерированный 16-значный пароль
6. Вставьте его в `.env` как `EMAIL_PASSWORD` (без пробелов)

### Для других почтовых сервисов:

**Yandex:**
```env
EMAIL_HOST=imap.yandex.ru
EMAIL_PORT=993
```

**Mail.ru:**
```env
EMAIL_HOST=imap.mail.ru
EMAIL_PORT=993
```

**Outlook/Hotmail:**
```env
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993
```

## Шаг 3: Запуск теста

```bash
python test_email.py
```

### Что делает тестовый скрипт:

1. **Тестирует подключение** к почтовому серверу
2. **Получает список папок** в вашем почтовом ящике
3. **Ищет непрочитанные письма** с вложениями
4. **Сохраняет резюме** в папку `data/resumes/`
5. **Показывает статистику** обработки

### Пример вывода:

```
============================================================
AI Recruiting Agent - Email Integration Test
============================================================
Testing Email Connection
============================================================
✓ Successfully connected to imap.gmail.com

Available folders (10):
  - INBOX
  - Sent
  - Drafts
  - Spam
  ...

============================================================
Fetching Resume Emails
============================================================
Searching for unread emails in 'INBOX'...

Found 3 unread email(s)

--- Email 1/3 ---
From: candidate@example.com
Subject: Application for Python Developer
Date: Mon, 30 Dec 2024 10:00:00 +0000
Attachments: 1

Attachments:
  - John_Doe_Resume.pdf (application/pdf)

✓ Saved 1 resume(s)

============================================================
Processing complete: 3 new resume(s) saved
============================================================

Statistics
============================================================

Total emails processed: 5
Total resumes saved: 5
Storage path: data/resumes
Supported formats: .pdf, .docx, .doc, .txt, .rtf

Saved resumes:
  - John_Doe_Resume.pdf (from: candidate@example.com)
  - Jane_Smith_CV.docx (from: jane@example.com)
  ...
```

## Шаг 4: Проверка результатов

Проверьте сохраненные резюме:

```bash
# Windows
dir data\resumes

# Linux/Mac
ls -la data/resumes/
```

Формат имени файла: `YYYYMMDD_HHMMSS_EmailID_OriginalName.ext`

Пример: `20241230_101500_12345_John_Doe_Resume.pdf`

## Структура данных

### Сохраненные резюме
```
data/resumes/
├── 20241230_101500_12345_John_Doe_Resume.pdf
├── 20241230_102000_12346_Jane_Smith_CV.docx
└── ...
```

### База обработанных писем
```
data/processed_emails.json
```

Этот файл отслеживает уже обработанные письма, чтобы избежать дубликатов.

## Troubleshooting

### ❌ "Authentication failed"

**Проблема:** Неверный логин или пароль

**Решение:**
- Проверьте EMAIL_ADDRESS и EMAIL_PASSWORD в `.env`
- Для Gmail убедитесь, что используете App Password, а не обычный пароль
- Проверьте, что включена двухфакторная аутентификация (для Gmail)

### ❌ "Connection refused"

**Проблема:** Не удается подключиться к серверу

**Решение:**
- Проверьте EMAIL_HOST и EMAIL_PORT
- Убедитесь, что IMAP включен в настройках почты
- Проверьте интернет-соединение
- Проверьте, не блокирует ли файрвол подключение

### ❌ "No module named 'imapclient'"

**Проблема:** Не установлены зависимости

**Решение:**
```bash
pip install -r requirements.txt
```

### ⚠️ "No unread emails found"

**Это нормально!** Значит в вашей почте нет непрочитанных писем с резюме.

**Для теста:**
1. Отправьте себе письмо с прикрепленным PDF/DOCX файлом
2. Не открывайте его (должно остаться непрочитанным)
3. Запустите `python test_email.py` снова

## Следующие шаги

После успешной интеграции с почтой можно приступать к:

1. ✅ **Парсингу резюме** - извлечение структурированных данных из PDF/DOCX
2. ✅ **Обработке вакансий** - парсинг описаний вакансий
3. ✅ **Модели сопоставления** - ML/NLP для matching резюме и вакансий
4. ✅ **API разработка** - REST API на FastAPI
5. ✅ **UI интерфейс** - веб-интерфейс на Streamlit

## Полезные команды

```bash
# Просмотр логов
python test_email.py 2>&1 | tee email_test.log

# Очистка данных (для повторного теста)
# Windows:
rmdir /s /q data
# Linux/Mac:
# rm -rf data/

# Проверка статуса обработки
python -c "from src.email_integration import AttachmentHandler; from src.config import settings; h = AttachmentHandler(settings.resume_storage_path, settings.processed_emails_db); print(h.get_processed_stats())"
```

## Документация

Подробная документация доступна в [docs/email_integration.md](docs/email_integration.md)
