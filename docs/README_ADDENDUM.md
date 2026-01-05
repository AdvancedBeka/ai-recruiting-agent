# Quick Usage Addendum

## API endpoints
- `/resumes/upload`, `/resumes`
- `/jobs`
- `/recommendations` (GET/POST) with `matcher_type`: `semantic`, `tfidf`, `cross_encoder`, `llm`, `tfidf_ml`

## Run locally
```bash
uvicorn src.api.app:app --port 8000
API_BASE_URL=http://localhost:8000 streamlit run streamlit_app.py
```

## Docker
```bash
docker-compose up --build
```
API on 8000, UI on 8501.

## cURL examples
```bash
curl -X POST "http://localhost:8000/resumes/upload?language=en" -F "file=@/path/to/resume.pdf"

curl -X POST "http://localhost:8000/jobs" -H "Content-Type: application/json" -d '{
  "title": "Python Engineer",
  "company": "Acme",
  "description": "FastAPI, Docker, PostgreSQL, AWS",
  "required_skills": ["Python","FastAPI","Docker","PostgreSQL","AWS"]
}'

curl "http://localhost:8000/recommendations?job_id=job_001&matcher_type=semantic&top_n=5&language=en"
```
