# AI Recruiting Agent — Report

## Summary
- Ingestion: IMAP email fetch + attachment handler, local storage.
- Parsing: PDF/DOCX/TXT, contacts/skills/summary/keywords, simple NER/TF-IDF, language autodetect (en/ru).
- Matching: semantic SBERT + cosine (+ FAISS), TF-IDF cosine, TF-IDF+ML (LogReg), cross-encoder zero-shot, LLM (OpenAI GPT) with score 0–1 + explanation, fallbacks and caching.
- API: FastAPI, ru/en, endpoints for resumes, jobs, recommendations (GET/POST).
- UI: Streamlit for upload, jobs, recommendations.
- Docker: API + Streamlit compose.

## Architecture & Flow
1) Email → IMAP fetch → attachments saved (`data/resumes/`) + metadata.
2) Parsing (`TextExtractor`):
   - Detect language (ru/en), extract text (PDF/DOCX/TXT).
   - Contacts (email/phone/LinkedIn/GitHub), skills, keywords (TF-IDF or fallback), summary.
   - Output `Resume` model with structured fields.
3) Matching:
   - Semantic: SBERT embeddings + cosine; FAISS index for fast top-K preselect.
   - TF-IDF: cosine; TF-IDF+ML (LogReg) optional saved model.
   - Cross-encoder: zero-shot rerank.
   - LLM: OpenAI GPT with JSON response (score 0–1 + reason) and fallback.
4) API: returns top-N candidates for a job (by ID or free text).
5) UI: Streamlit to upload resumes, create jobs, run recommendations.

## Processing Steps (Resume)
1. `POST /resumes/upload` saves temp file.
2. `TextExtractor.parse_resume` parses text, detects language, extracts contacts/skills/summary/keywords.
3. `Resume` stored in memory (API storage) for matching.

## API Examples
Upload resume:
```bash
curl -X POST "http://localhost:8000/resumes/upload?language=en" \
  -F "file=@/path/to/resume.pdf"
```

Create job:
```bash
curl -X POST "http://localhost:8000/jobs" -H "Content-Type: application/json" -d '{
  "title": "Senior Python Engineer",
  "company": "Acme",
  "description": "Backend services with FastAPI, Docker, PostgreSQL, AWS",
  "required_skills": ["Python","FastAPI","Docker","PostgreSQL","AWS"],
  "nice_to_have_skills": ["Redis","CI/CD"]
}'
```

Recommendations (semantic):
```bash
curl "http://localhost:8000/recommendations?job_id=job_001&matcher_type=semantic&top_n=5&language=en"
```

Recommendations with custom job (LLM):
```bash
curl -X POST "http://localhost:8000/recommendations" -H "Content-Type: application/json" -d '{
  "job_description": "Looking for backend Python/FastAPI engineer with Docker and AWS",
  "title": "Backend Engineer",
  "required_skills": ["Python","FastAPI","Docker","AWS"],
  "matcher_type": "llm",
  "top_n": 5,
  "language": "en"
}'
```

## Matchers
- `semantic`: SBERT + cosine, FAISS preselect when index exists.
- `tfidf`: TF-IDF cosine (lang-aware stop words).
- `tfidf_ml`: TF-IDF + LogReg (demo model saved at `data/models/tfidf_ml_model.joblib`).
- `cross_encoder`: zero-shot cross-encoder rerank.
- `llm`: OpenAI GPT, score 0–1 + explanation; fallback to skills/keywords if API not available.

## Running
- API: `uvicorn src.api.app:app --port 8000`
- Streamlit: `API_BASE_URL=http://localhost:8000 streamlit run streamlit_app.py`
- Docker: `docker-compose up --build` (api:8000, frontend:8501)

## UI Notes
- Upload shows extracted skills/keywords immediately.
- Create job → select matcher → get top candidates with scores and matched/missing skills.

## Next Steps
- Cron/worker for periodic email fetch and FAISS index refresh.
- Proper eval notebook with metrics on a labeled set (when available).
