# Архитектура AI Recruiting Agent

## Обзор системы

AI Recruiting Agent - это модульная система для автоматизации процесса рекрутинга, состоящая из нескольких независимых компонентов.

## Компоненты системы

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Recruiting Agent                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌─────────────┐
│   Email      │    │  Resume Parser   │    │  Matching   │
│ Integration  │───▶│   & Storage      │───▶│   Engine    │
└──────────────┘    └──────────────────┘    └─────────────┘
        │                     │                     │
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   REST API       │
                    │   + Frontend     │
                    └──────────────────┘
```

## 1. Email Integration Module

**Текущий статус:** ✅ Реализован

### Функции:
- Подключение к IMAP серверу
- Получение непрочитанных писем
- Извлечение вложений (резюме)
- Сохранение файлов с метаданными
- Отслеживание обработанных писем

### Компоненты:

#### EmailClient
```python
EmailClient(host, port, email, password)
├── connect()           # Подключение к IMAP
├── fetch_unread_emails()  # Получение писем
├── mark_as_read()      # Пометка как прочитанное
└── disconnect()        # Отключение
```

#### AttachmentHandler
```python
AttachmentHandler(storage_path, db_path)
├── process_attachments()   # Обработка вложений
├── is_email_processed()    # Проверка дубликатов
├── get_processed_stats()   # Статистика
└── get_all_resumes()       # Список резюме
```

### Поток данных:

```
Email Server (IMAP)
        │
        ▼
┌─────────────────┐
│  EmailClient    │  Получение писем
│  - Fetch emails │
│  - Parse MIME   │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ AttachmentHandler   │  Обработка вложений
│ - Extract files     │
│ - Validate format   │
│ - Calculate hash    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  File Storage       │  Сохранение
│  data/resumes/      │
│  + metadata in JSON │
└─────────────────────┘
```

### Файловая структура:

```
data/
├── resumes/
│   ├── 20241230_101500_12345_John_Doe_Resume.pdf
│   ├── 20241230_102000_12346_Jane_Smith_CV.docx
│   └── ...
└── processed_emails.json
```

## 2. Resume Parser Module

**Текущий статус:** 🚧 Планируется

### Функции:
- Извлечение текста из PDF, DOCX, TXT
- NLP обработка (токенизация, NER)
- Структурирование данных
- Извлечение ключевых навыков

### Планируемая структура:

```python
ResumeParser
├── PDFParser          # PyPDF2, pdfplumber
├── DOCXParser         # python-docx
├── TextExtractor      # Извлечение текста
├── NERExtractor       # Named Entity Recognition
│   ├── Skills         # Навыки
│   ├── Experience     # Опыт работы
│   ├── Education      # Образование
│   └── Contact        # Контакты
└── KeywordExtractor   # TF-IDF, RAKE
```

### Выходной формат:

```json
{
  "resume_id": "uuid",
  "file_path": "path/to/resume.pdf",
  "parsed_date": "2024-12-30T10:00:00",
  "candidate": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "skills": ["Python", "FastAPI", "Docker", "SQL"],
  "experience": [
    {
      "position": "Senior Python Developer",
      "company": "Tech Corp",
      "duration": "2020-2023",
      "description": "..."
    }
  ],
  "education": [
    {
      "degree": "Master of Computer Science",
      "institution": "University",
      "year": "2020"
    }
  ],
  "summary": "Extracted summary text...",
  "keywords": ["python", "api", "microservices"]
}
```

## 3. Matching Engine

**Текущий статус:** 🚧 Планируется

### Три подхода к сопоставлению:

#### Подход 1: Семантическое сравнение
```python
SemanticMatcher
├── EmbeddingModel     # Sentence-BERT / USE
├── VectorStore        # FAISS / ChromaDB
├── calculate_similarity()  # Cosine similarity
└── rank_candidates()
```

**Алгоритм:**
1. Преобразование резюме → векторы (embeddings)
2. Преобразование вакансии → вектор
3. Вычисление cosine similarity
4. Ранжирование по релевантности

#### Подход 2: TF-IDF + ML
```python
TFIDFMatcher
├── TfidfVectorizer    # scikit-learn
├── Classifier         # LogisticRegression / SVM
├── fit()              # Обучение на размеченных данных
└── predict()          # Предсказание релевантности
```

**Алгоритм:**
1. TF-IDF векторизация текста
2. Обучение классификатора
3. Предсказание match/no-match
4. Ранжирование по вероятности

#### Подход 3: LLM-based
```python
LLMMatcher
├── LLMClient          # OpenAI / Anthropic / Local
├── PromptTemplate     # Шаблоны промптов
├── match_with_explanation()
└── batch_match()
```

**Промпт:**
```
Проанализируй соответствие резюме кандидата требованиям вакансии.

Вакансия: {job_description}
Резюме: {resume_text}

Оцени релевантность от 0 до 1 и объясни почему.
Формат ответа: {"score": 0.85, "reasoning": "..."}
```

### Сравнение подходов:

| Подход | Точность | Скорость | Стоимость | Объяснимость |
|--------|----------|----------|-----------|--------------|
| Semantic | Высокая | Быстро | Низкая | Средняя |
| TF-IDF+ML | Средняя | Очень быстро | Низкая | Низкая |
| LLM | Очень высокая | Медленно | Высокая | Очень высокая |

## 4. REST API

**Текущий статус:** 🚧 Планируется

### Endpoints:

```
POST   /api/v1/jobs              # Создать вакансию
GET    /api/v1/jobs              # Список вакансий
GET    /api/v1/jobs/{id}         # Детали вакансии

GET    /api/v1/resumes           # Список резюме
GET    /api/v1/resumes/{id}      # Детали резюме

GET    /api/v1/match?job_id={id} # Поиск кандидатов
POST   /api/v1/match             # Batch matching
```

### Архитектура FastAPI:

```
api/
├── main.py              # FastAPI app
├── routes/
│   ├── jobs.py
│   ├── resumes.py
│   └── matching.py
├── models/
│   ├── job.py
│   ├── resume.py
│   └── match.py
├── services/
│   ├── job_service.py
│   ├── resume_service.py
│   └── matching_service.py
└── dependencies.py
```

## 5. Frontend (Streamlit)

**Текущий статус:** 🚧 Планируется

### Страницы:

1. **Dashboard**
   - Общая статистика
   - График поступления резюме
   - Топ вакансии

2. **Resumes**
   - Список резюме
   - Фильтры и поиск
   - Детальный просмотр

3. **Jobs**
   - Список вакансий
   - Создание/редактирование
   - Просмотр кандидатов

4. **Matching**
   - Выбор вакансии
   - Выбор метода matching
   - Результаты с объяснениями

## Технологический стек

### Текущий (Реализовано)
- **Python 3.10+**
- **Email**: imapclient, email-validator
- **Config**: pydantic-settings, python-dotenv
- **Data**: pandas, numpy

### Планируемый

#### NLP/ML:
- **Парсинг**: PyPDF2, python-docx, pdfplumber
- **NLP**: spaCy, nltk
- **Embeddings**: sentence-transformers, openai
- **ML**: scikit-learn
- **Vector DB**: FAISS, ChromaDB

#### Backend:
- **API**: FastAPI, uvicorn
- **Database**: PostgreSQL, SQLAlchemy
- **Cache**: Redis
- **Task Queue**: Celery

#### Frontend:
- **UI**: Streamlit
- **Visualization**: plotly, altair

#### DevOps:
- **Containerization**: Docker, docker-compose
- **Orchestration**: Kubernetes (опционально)
- **Monitoring**: Prometheus, Grafana

## Паттерны проектирования

### 1. Strategy Pattern
Для выбора метода matching:
```python
class MatchingStrategy(ABC):
    @abstractmethod
    def match(self, resume, job) -> float:
        pass

class SemanticStrategy(MatchingStrategy): ...
class TFIDFStrategy(MatchingStrategy): ...
class LLMStrategy(MatchingStrategy): ...
```

### 2. Factory Pattern
Для создания парсеров:
```python
class ParserFactory:
    @staticmethod
    def create_parser(file_extension):
        if file_extension == '.pdf':
            return PDFParser()
        elif file_extension == '.docx':
            return DOCXParser()
        ...
```

### 3. Repository Pattern
Для работы с данными:
```python
class ResumeRepository:
    def save(self, resume): ...
    def find_by_id(self, id): ...
    def find_all(self): ...
```

## Масштабируемость

### Horizontal Scaling
- API: Multiple FastAPI instances + Load Balancer
- Matching: Task queue (Celery) + multiple workers
- Storage: S3/MinIO for file storage

### Caching Strategy
- Redis для кэширования embeddings
- In-memory cache для часто используемых вакансий
- CDN для статических файлов

### Мониторинг
- Request/Response logging
- Performance metrics (response time, throughput)
- Error tracking (Sentry)
- Resource monitoring (CPU, Memory, Disk)

## Безопасность

1. **Аутентификация**: JWT tokens
2. **Авторизация**: RBAC (Role-Based Access Control)
3. **Data encryption**: TLS/SSL, encrypted storage
4. **Input validation**: Pydantic models
5. **Rate limiting**: API throttling
6. **CORS**: Настройка разрешенных origins

## Дальнейшее развитие

### Phase 1: MVP (Текущая фаза)
- ✅ Email integration
- 🚧 Resume parsing
- 🚧 Basic matching (1 подход)
- 🚧 Simple API

### Phase 2: Core Features
- Advanced matching (3 подхода)
- Streamlit UI
- Database integration
- Batch processing

### Phase 3: Production Ready
- User authentication
- Advanced analytics
- Email notifications
- Automatic resume updates
- A/B testing для методов matching

### Phase 4: Scale
- Multi-tenancy
- Advanced ML models
- Real-time processing
- Integration с ATS системами
