"""
Pydantic models for API requests and responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class JobCreate(BaseModel):
    """Job creation request"""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Full job description")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    nice_to_have_skills: List[str] = Field(default_factory=list, description="Nice to have skills")
    location: Optional[str] = Field(None, description="Job location")
    salary_range: Optional[str] = Field(None, description="Salary range")


class JobResponse(BaseModel):
    """Job response"""
    job_id: str
    title: str
    company: str
    description: str
    required_skills: List[str]
    nice_to_have_skills: List[str]
    location: Optional[str] = None
    salary_range: Optional[str] = None
    created_at: datetime


class CandidateMatch(BaseModel):
    """Candidate match result"""
    resume_id: str
    candidate_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    overall_score: float = Field(..., ge=0.0, le=1.0)
    skills_match: float = Field(..., ge=0.0, le=1.0)
    semantic_similarity: float = Field(..., ge=0.0, le=1.0)
    matched_skills: List[str]
    missing_skills: List[str]
    matching_method: str
    explanation: Optional[str] = None


class RecommendationsRequest(BaseModel):
    """Request for job recommendations"""
    job_id: Optional[str] = Field(None, description="Job ID from database")
    job_description: Optional[str] = Field(None, description="Direct job description text")
    title: Optional[str] = Field(None, description="Job title (if using job_description)")
    required_skills: Optional[List[str]] = Field(None, description="Required skills (if using job_description)")
    top_n: int = Field(5, ge=1, le=50, description="Number of top candidates to return")
    matcher_type: str = Field(
        "semantic",
        description="Matcher type: semantic, tfidf, tfidf_ml, cross_encoder, llm, gemini"
    )
    language: str = Field("en", description="Response language: en or ru")


class RecommendationsResponse(BaseModel):
    """Recommendations response"""
    job_id: Optional[str]
    job_title: str
    matcher_used: str
    language: str
    total_candidates: int
    top_candidates: List[CandidateMatch]
    processing_time_seconds: float


class UploadResponse(BaseModel):
    """File upload response"""
    success: bool
    resume_id: str
    candidate_name: Optional[str]
    message: str
    extracted_skills: List[str]
    extracted_keywords: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    components: Dict[str, str]
    total_resumes: int
    total_jobs: int


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
