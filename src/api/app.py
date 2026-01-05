"""
FastAPI REST API for AI Recruiting Agent

Endpoints:
- POST /resumes/upload - Upload resume file
- GET /jobs - List all jobs
- POST /jobs - Create new job
- GET /jobs/{job_id} - Get job details
- GET /recommendations - Get top candidates for a job
- GET /health - Health check
"""
import sys
from pathlib import Path
import time
import tempfile
from typing import List, Optional
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.models import (
    JobCreate,
    JobResponse,
    RecommendationsRequest,
    RecommendationsResponse,
    CandidateMatch,
    UploadResponse,
    HealthResponse,
    ErrorResponse,
)
from api.storage import resume_storage, job_storage
from api.translations import translate

from resume_parser import TextExtractor
from matching import (
    SemanticMatcher,
    TFIDFMatcher,
    TfidfMLMatcher,
    CrossEncoderMatcher,
    LLMMatcher,
    Job,
    MatchResult,
)
from config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Recruiting Agent API",
    description="REST API for intelligent resume matching and candidate recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
settings = Settings()
text_extractor = TextExtractor(use_nlp=True)

# Initialize matchers
matchers = {
    "semantic": None,
    "tfidf": None,
    "tfidf_ml": None,
    "cross_encoder": None,
    "llm": None,
}


def get_matcher(matcher_type: str):
    """Get or initialize matcher"""
    if matchers[matcher_type] is None:
        if matcher_type == "semantic":
            matchers[matcher_type] = SemanticMatcher()
        elif matcher_type == "tfidf":
            matchers[matcher_type] = TFIDFMatcher()
        elif matcher_type == "tfidf_ml":
            matchers[matcher_type] = TfidfMLMatcher()
        elif matcher_type == "cross_encoder":
            matchers[matcher_type] = CrossEncoderMatcher()
        elif matcher_type == "llm":
            matchers[matcher_type] = LLMMatcher(api_key=settings.openai_api_key)

    return matchers[matcher_type]


@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI Recruiting Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "resume_parser": "ready",
            "semantic_matcher": "ready",
            "tfidf_matcher": "ready",
            "tfidf_ml_matcher": "ready" if matchers.get("tfidf_ml") else "not initialized",
            "cross_encoder_matcher": "ready" if matchers.get("cross_encoder") else "not initialized",
            "llm_matcher": "available" if settings.openai_api_key else "not configured",
        },
        "total_resumes": resume_storage.count(),
        "total_jobs": job_storage.count(),
    }


@app.post("/resumes/upload", response_model=UploadResponse, tags=["Resumes"])
async def upload_resume(file: UploadFile = File(...), language: str = Query("en", regex="^(en|ru)$")):
    """
    Upload and parse a resume file

    Supported formats: PDF, DOCX, TXT
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".txt"]
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, detail=translate("invalid_file_type", language)
        )

    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Parse resume
        resume = text_extractor.parse_resume(tmp_path)

        # Delete temp file
        Path(tmp_path).unlink()

        if not resume:
            raise HTTPException(
                status_code=400, detail=translate("upload_failed", language)
            )

        # Store resume
        resume_id = resume_storage.add_resume(resume)

        return {
            "success": True,
            "resume_id": resume_id,
            "candidate_name": resume.contact_info.name,
            "message": translate("upload_success", language),
            "extracted_skills": resume.skills[:20],
            "extracted_keywords": resume.keywords[:20],
        }

    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resumes", tags=["Resumes"])
async def list_resumes():
    """List all uploaded resumes"""
    resumes = resume_storage.get_all_resumes()

    return {
        "total": len(resumes),
        "resumes": [
            {
                "resume_id": r.file_name,
                "name": r.contact_info.name,
                "email": r.contact_info.email,
                "phone": r.contact_info.phone,
                "skills_count": len(r.skills),
                "keywords_count": len(r.keywords),
            }
            for r in resumes
        ],
    }


@app.get("/jobs", tags=["Jobs"])
async def list_jobs():
    """List all jobs"""
    jobs = job_storage.get_all_jobs()

    return {
        "total": len(jobs),
        "jobs": jobs,
    }


@app.post("/jobs", response_model=JobResponse, tags=["Jobs"])
async def create_job(job: JobCreate):
    """Create a new job posting"""
    # Generate job ID
    job_id = f"job_{int(time.time())}"

    job_storage.add_job(
        job_id=job_id,
        title=job.title,
        company=job.company,
        description=job.description,
        required_skills=job.required_skills,
        nice_to_have_skills=job.nice_to_have_skills,
        location=job.location,
        salary_range=job.salary_range,
    )

    job_data = job_storage.get_job(job_id)

    return JobResponse(
        job_id=job_data["job_id"],
        title=job_data["title"],
        company=job_data["company"],
        description=job_data["description"],
        required_skills=job_data["required_skills"],
        nice_to_have_skills=job_data["nice_to_have_skills"],
        location=job_data.get("location"),
        salary_range=job_data.get("salary_range"),
        created_at=job_data["created_at"],
    )


@app.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def get_job(job_id: str):
    """Get job details by ID"""
    job_data = job_storage.get_job(job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(
        job_id=job_data["job_id"],
        title=job_data["title"],
        company=job_data["company"],
        description=job_data["description"],
        required_skills=job_data["required_skills"],
        nice_to_have_skills=job_data["nice_to_have_skills"],
        location=job_data.get("location"),
        salary_range=job_data.get("salary_range"),
        created_at=job_data["created_at"],
    )


@app.post("/recommendations", response_model=RecommendationsResponse, tags=["Recommendations"])
async def get_recommendations(request: RecommendationsRequest):
    """
    Get top candidate recommendations for a job (POST body).
    """
    return await _compute_recommendations(request)


@app.get("/recommendations", response_model=RecommendationsResponse, tags=["Recommendations"])
async def get_recommendations_get(
    job_id: Optional[str] = Query(None),
    job_description: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    required_skills: Optional[List[str]] = Query(None),
    top_n: int = Query(5, ge=1, le=50),
    matcher_type: str = Query("semantic"),
    language: str = Query("en"),
):
    """
    Get top candidate recommendations for a job

    You can specify either:
    - job_id: Use existing job from database
    - job_description + title + required_skills: Use custom job description
    """
    req = RecommendationsRequest(
        job_id=job_id,
        job_description=job_description,
        title=title,
        required_skills=required_skills,
        top_n=top_n,
        matcher_type=matcher_type,
        language=language,
    )
    return await _compute_recommendations(req)


async def _compute_recommendations(request: RecommendationsRequest):
    start_time = time.time()

    # Determine job
    job = None

    if request.job_id:
        # Get job from storage
        job = job_storage.get_job_as_model(request.job_id)
        if not job:
            raise HTTPException(
                status_code=404, detail=translate("job_not_found", request.language)
            )
        job_title = job.title
        job_id = request.job_id

    elif request.job_description:
        # Create job from description
        job_id = "custom_job"
        job_title = request.title or "Custom Job"
        job = Job(
            job_id=job_id,
            title=job_title,
            company="Custom",
            description=request.job_description,
            required_skills=request.required_skills or [],
            nice_to_have_skills=[],
        )

    else:
        raise HTTPException(
            status_code=400, detail=translate("no_job_specified", request.language)
        )

    # Get all resumes
    resumes = resume_storage.get_all_resumes()

    if not resumes:
        raise HTTPException(
            status_code=404, detail=translate("no_resumes", request.language)
        )

    # Get matcher
    try:
        matcher = get_matcher(request.matcher_type)
    except KeyError:
        raise HTTPException(
            status_code=400, detail=translate("matcher_not_available", request.language)
        )
    if request.matcher_type == "tfidf_ml" and hasattr(matcher, "is_trained") and not matcher.is_trained:
        raise HTTPException(
            status_code=503,
            detail="TF-IDF ML matcher is not trained. Train and save a model before using this matcher.",
        )

    # Match all resumes
    results: List[MatchResult] = []

    for resume in resumes:
        try:
            result = matcher.match(resume, job)
            results.append(result)
        except Exception as e:
            logger.error(f"Error matching resume {resume.file_name}: {e}")

    # Sort by overall score
    results.sort(key=lambda x: x.overall_score, reverse=True)

    # Get top N
    top_results = results[: request.top_n]

    # Convert to response format
    candidates = []

    for result in top_results:
        resume = resume_storage.get_resume(result.resume_id)

        candidates.append(
            CandidateMatch(
                resume_id=result.resume_id,
                candidate_name=resume.contact_info.name if resume else None,
                email=resume.contact_info.email if resume else None,
                phone=resume.contact_info.phone if resume else None,
                overall_score=result.overall_score,
                skills_match=result.skills_match,
                semantic_similarity=result.semantic_similarity,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                matching_method=result.matching_method,
                explanation=result.explanation,
            )
        )

    processing_time = time.time() - start_time

    return RecommendationsResponse(
        job_id=job_id if request.job_id else None,
        job_title=job_title,
        matcher_used=request.matcher_type,
        language=request.language,
        total_candidates=len(results),
        top_candidates=candidates,
        processing_time_seconds=round(processing_time, 2),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
