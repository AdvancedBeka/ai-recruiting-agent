# AI Recruiting Agent - REST API Documentation

FastAPI-based REST API for intelligent resume matching and candidate recommendations.

## Features

✅ **Resume Management**
- Upload resumes (PDF, DOCX, TXT)
- Automatic parsing and skill extraction
- NLP-based text processing

✅ **Job Management**
- Create and manage job postings
- Store required skills and job descriptions
- Pre-loaded sample jobs for testing

✅ **Intelligent Matching**
- 4 matching algorithms: Semantic (BERT), TF-IDF, OpenAI GPT-4o, Google Gemini 2.5 Pro
- Get top N candidates for any job
- Detailed match explanations

✅ **Multi-language Support**
- English and Russian
- Localized error messages and responses

✅ **Production Ready**
- Health check endpoint
- CORS support
- Auto-generated OpenAPI docs (Swagger)
- Type-safe with Pydantic models

---

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn python-multipart
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python run_api.py
```

Server will start at: http://localhost:8000

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 4. Test the API

```bash
# In another terminal
python test_api.py
```

---

## API Endpoints

### General

#### `GET /`
Root endpoint with API info

#### `GET /health`
Health check and component status

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "resume_parser": "ready",
    "semantic_matcher": "ready",
    "tfidf_matcher": "ready",
    "llm_matcher": "available",
    "gemini_matcher": "not configured"
  },
  "total_resumes": 5,
  "total_jobs": 8
}
```

---

### Resumes

#### `POST /resumes/upload`
Upload and parse a resume file

**Parameters:**
- `file` (form-data): Resume file (PDF, DOCX, TXT)
- `language` (query): Response language (`en` or `ru`)

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/resumes/upload?language=en" \
  -F "file=@resume.pdf"
```

**Example (Python):**
```python
import requests

with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/resumes/upload',
        files={'file': f},
        params={'language': 'en'}
    )

print(response.json())
```

**Response:**
```json
{
  "success": true,
  "resume_id": "resume.pdf",
  "candidate_name": "John Doe",
  "message": "Resume uploaded and parsed successfully",
  "extracted_skills": ["Python", "Machine Learning", "Docker", ...],
  "extracted_keywords": ["engineer", "ml", "ai", ...]
}
```

#### `GET /resumes`
List all uploaded resumes

**Response:**
```json
{
  "total": 3,
  "resumes": [
    {
      "resume_id": "resume1.pdf",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0100",
      "skills_count": 15,
      "keywords_count": 25
    }
  ]
}
```

---

### Jobs

#### `GET /jobs`
List all jobs

**Response:**
```json
{
  "total": 5,
  "jobs": [
    {
      "job_id": "job_001",
      "title": "Senior Python Backend Developer",
      "company": "Tech Corp",
      "description": "...",
      "required_skills": ["Python", "Django", ...],
      "nice_to_have_skills": ["Machine Learning", ...],
      "location": "Remote",
      "salary_range": "$100k - $150k",
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

#### `POST /jobs`
Create a new job posting

**Request Body:**
```json
{
  "title": "Senior ML Engineer",
  "company": "AI Corp",
  "description": "We're looking for...",
  "required_skills": ["Python", "PyTorch", "Docker"],
  "nice_to_have_skills": ["Kubernetes", "MLOps"],
  "location": "Remote",
  "salary_range": "$120k - $180k"
}
```

**Response:**
```json
{
  "job_id": "job_1737889200",
  "title": "Senior ML Engineer",
  ...
}
```

#### `GET /jobs/{job_id}`
Get job details by ID

**Response:**
```json
{
  "job_id": "job_001",
  "title": "Senior Python Backend Developer",
  "company": "Tech Corp",
  ...
}
```

---

### Recommendations

#### `POST /recommendations`
Get top candidate recommendations for a job

**Request Body (Option 1 - Using existing job):**
```json
{
  "job_id": "job_001",
  "top_n": 5,
  "matcher_type": "semantic",
  "language": "en"
}
```

**Request Body (Option 2 - Using custom job description):**
```json
{
  "job_description": "Looking for a Python developer with ML experience...",
  "title": "Python ML Developer",
  "required_skills": ["Python", "Machine Learning", "PyTorch"],
  "top_n": 5,
  "matcher_type": "semantic",
  "language": "ru"
}
```

**Parameters:**
- `job_id` (optional): Use existing job from database
- `job_description` (optional): Custom job description
- `title` (optional): Job title for custom job
- `required_skills` (optional): Required skills for custom job
- `top_n` (int): Number of candidates to return (1-50, default: 5)
- `matcher_type` (string): `semantic`, `tfidf`, `llm`, or `gemini`
- `language` (string): `en` or `ru`

**Matcher Types:**
- `semantic` - Sentence-BERT (94% accuracy, FREE, no API key needed) **⭐ RECOMMENDED**
- `tfidf` - TF-IDF + cosine similarity (basic, fast)
- `llm` - OpenAI GPT-4o (requires `OPENAI_API_KEY` in .env)
- `gemini` - Google Gemini 2.5 Pro (requires `GOOGLE_API_KEY` in .env)

**Example (Python):**
```python
import requests

# Option 1: Use existing job
response = requests.post('http://localhost:8000/recommendations', json={
    "job_id": "job_001",
    "top_n": 5,
    "matcher_type": "semantic",
    "language": "en"
})

# Option 2: Custom job description
response = requests.post('http://localhost:8000/recommendations', json={
    "job_description": "Looking for Python ML engineer...",
    "title": "ML Engineer",
    "required_skills": ["Python", "PyTorch", "Docker"],
    "top_n": 3,
    "matcher_type": "semantic",
    "language": "ru"
})

print(response.json())
```

**Response:**
```json
{
  "job_id": "job_001",
  "job_title": "Senior Python Backend Developer",
  "matcher_used": "semantic",
  "language": "en",
  "total_candidates": 10,
  "top_candidates": [
    {
      "resume_id": "resume1.pdf",
      "candidate_name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0100",
      "overall_score": 0.85,
      "skills_match": 0.75,
      "semantic_similarity": 0.92,
      "matched_skills": ["Python", "Django", "PostgreSQL", ...],
      "missing_skills": ["Kubernetes"],
      "matching_method": "semantic",
      "explanation": "Strong match based on Python backend experience..."
    }
  ],
  "processing_time_seconds": 1.23
}
```

---

## Error Handling

All errors return JSON with error details:

```json
{
  "error": "Job not found",
  "detail": "No job with ID 'job_999'",
  "code": "NOT_FOUND"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Multi-language Support

The API supports English and Russian. Set the `language` parameter:

**English:**
```bash
curl "http://localhost:8000/resumes/upload?language=en" -F "file=@resume.pdf"
```

**Russian:**
```bash
curl "http://localhost:8000/resumes/upload?language=ru" -F "file=@resume.pdf"
```

---

## Configuration

Create a `.env` file for optional configurations:

```bash
# OpenAI (for LLM matcher)
OPENAI_API_KEY=sk-your-key-here

# Google AI Studio (for Gemini matcher)
GOOGLE_API_KEY=your-key-here

# Storage paths
RESUME_STORAGE_PATH=./data/resumes
PROCESSED_EMAILS_DB=./data/processed_emails.json
```

---

## Testing

### Automated Tests

Run the test suite:
```bash
python test_api.py
```

This will test:
1. ✅ Health check
2. ✅ List jobs
3. ✅ Upload resume
4. ✅ Create job
5. ✅ Get recommendations (existing job)
6. ✅ Get recommendations (custom job)

### Interactive Testing

Open Swagger UI at http://localhost:8000/docs and try endpoints interactively.

---

## Production Deployment

### Using Uvicorn

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker (see Docker documentation)

```bash
docker build -t ai-recruiting-agent .
docker run -p 8000:8000 ai-recruiting-agent
```

---

## Performance

**Matching Speed:**
- Semantic (BERT): ~0.5s per resume
- TF-IDF: ~0.1s per resume
- LLM (GPT-4o): ~2-3s per resume
- Gemini 2.5 Pro: ~2-3s per resume

**Recommendations:**
- Use `semantic` matcher for best balance of speed and accuracy
- Use `tfidf` for fastest results (basic matching)
- Use `llm` or `gemini` for detailed explanations (slower, requires API keys)

---

## API Limits

**Built-in matchers (semantic, tfidf):**
- No limits, runs locally
- FREE to use

**External matchers (llm, gemini):**
- Subject to API provider limits
- OpenAI: Pay-per-use
- Google Gemini: 15 RPM, 1500 RPD (free tier)

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP/JSON
┌──────▼──────┐
│  FastAPI    │
│   Router    │
└──────┬──────┘
       │
┌──────▼───────────────────────┐
│  Business Logic Layer        │
│  - Resume Parser             │
│  - Matchers (BERT/TF-IDF/LLM)│
│  - Job Storage               │
└──────┬───────────────────────┘
       │
┌──────▼──────┐
│  Storage    │
│  (In-Memory)│
└─────────────┘
```

---

## Next Steps

1. **Add Database**: Replace in-memory storage with PostgreSQL/MongoDB
2. **Add Authentication**: JWT tokens, API keys
3. **Add Rate Limiting**: Prevent abuse
4. **Add Caching**: Cache matcher results
5. **Add Async Tasks**: Use Celery for long-running matches
6. **Add Monitoring**: Prometheus, Grafana
7. **Add Frontend**: Streamlit UI (see frontend documentation)

---

## Support

For issues and questions:
- Check Swagger docs: http://localhost:8000/docs
- Run tests: `python test_api.py`
- Check logs in console output

---

## License

See project LICENSE file.
