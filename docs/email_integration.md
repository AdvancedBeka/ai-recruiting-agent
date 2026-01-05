# Email Integration Documentation

## Обзор

Модуль email integration обеспечивает автоматическое получение резюме из почтового ящика через IMAP протокол.

## Компоненты

### 1. EmailClient

Класс для подключения к IMAP серверу и получения писем.

**Основные методы:**

- `connect()` - подключение к серверу
- `disconnect()` - отключение от сервера
- `fetch_unread_emails()` - получение непрочитанных писем
- `mark_as_read()` - пометить письмо как прочитанное
- `get_folder_list()` - список доступных папок

**Пример использования:**

```python
from email_integration import EmailClient

client = EmailClient(
    host="imap.gmail.com",
    port=993,
    email_address="cv@company.com",
    password="app_password"
)

with client:
    emails = client.fetch_unread_emails(folder="INBOX", limit=10)
    for email_data in emails:
        print(f"From: {email_data['from']}")
        print(f"Subject: {email_data['subject']}")
```

### 2. AttachmentHandler

Класс для обработки и сохранения вложений из писем.

**Основные методы:**

- `process_attachments()` - обработка вложений из письма
- `is_email_processed()` - проверка, обработано ли письмо
- `get_processed_stats()` - статистика обработки
- `get_all_resumes()` - список всех сохраненных резюме

**Пример использования:**

```python
from email_integration import AttachmentHandler

handler = AttachmentHandler(
    storage_path="./data/resumes",
    processed_db_path="./data/processed_emails.json"
)

# Обработка вложений
processed = handler.process_attachments(email_data)
print(f"Saved {len(processed)} resume(s)")

# Статистика
stats = handler.get_processed_stats()
print(f"Total resumes: {stats['total_resumes_saved']}")
```

## Поддерживаемые форматы

- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Текст (.txt)
- RTF (.rtf)

## Структура данных

### Email Data Dictionary

```python
{
    'id': 12345,
    'from': 'candidate@example.com',
    'to': 'cv@company.com',
    'subject': 'Application for Python Developer',
    'date': 'Mon, 30 Dec 2024 10:00:00 +0000',
    'body': 'Email body text...',
    'attachments': [
        {
            'filename': 'resume.pdf',
            'content_type': 'application/pdf',
            'data': b'...'
        }
    ],
    'has_attachments': True
}
```

### Processed Attachment Info

```python
{
    'original_filename': 'resume.pdf',
    'email_id': 12345,
    'email_from': 'candidate@example.com',
    'email_subject': 'Application for Python Developer',
    'email_date': 'Mon, 30 Dec 2024 10:00:00 +0000',
    'content_type': 'application/pdf',
    'file_size': 102400,
    'processed_date': '2024-12-30T10:15:00',
    'saved_path': './data/resumes/20241230_101500_12345_resume.pdf',
    'file_hash': 'sha256_hash_here'
}
```

## База данных обработанных писем

Система отслеживает обработанные письма в JSON файле `processed_emails.json`:

```json
{
  "12345": {
    "from": "candidate@example.com",
    "subject": "Application for Python Developer",
    "date": "Mon, 30 Dec 2024 10:00:00 +0000",
    "processed_date": "2024-12-30T10:15:00",
    "attachments": [...]
  }
}
```

Это предотвращает повторную обработку уже сохраненных резюме.

## Настройка для Gmail

### 1. Включите IMAP

1. Откройте Gmail Settings
2. Перейдите в Forwarding and POP/IMAP
3. Включите IMAP access

### 2. Создайте App Password

1. Перейдите на https://myaccount.google.com/security
2. Включите 2-Step Verification
3. Создайте App Password
4. Используйте сгенерированный пароль в `.env`

### 3. Конфигурация

```env
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## Обработка ошибок

Модуль включает обработку следующих ошибок:

- Ошибки подключения к IMAP серверу
- Ошибки аутентификации
- Ошибки парсинга писем
- Ошибки декодирования вложений
- Ошибки сохранения файлов

Все ошибки логируются через стандартный модуль `logging`.

## Безопасность

- Пароли хранятся только в `.env` файле (не коммитится в git)
- Имена файлов санитизируются перед сохранением
- Вычисляется SHA256 хеш для дедупликации файлов
- Поддержка SSL/TLS соединений

## Производительность

- Используется пакетное получение писем
- Опциональное ограничение количества обрабатываемых писем
- Кеширование информации об обработанных письмах
- Контекстный менеджер для автоматического управления соединениями
