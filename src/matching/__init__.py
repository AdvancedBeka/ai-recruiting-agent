"""
Matching Module - Resume to Job Matching Engine

Поддерживает четыре подхода к сопоставлению:
1. Semantic Matcher - Sentence-BERT embeddings + cosine similarity
2. TF-IDF Matcher - TF-IDF векторизация + cosine similarity
3. LLM Matcher - OpenAI GPT с объяснениями
4. Gemini Matcher - Google Gemini 2.0 Flash via Vertex AI

Usage:
    from matching import SemanticMatcher, TFIDFMatcher, LLMMatcher, GeminiMatcher, Job, MatchResult

    # Create matcher
    matcher = SemanticMatcher()
    # Or use Gemini
    gemini_matcher = GeminiMatcher(project_id="your-project-id")

    # Create job
    job = Job(
        job_id="job_001",
        title="Python Developer",
        description="Looking for Python expert...",
        required_skills=["Python", "Django", "PostgreSQL"]
    )

    # Match resume
    result = matcher.match(resume, job)
    print(f"Match score: {result.overall_score:.1%}")
"""

from .job_model import Job, MatchResult
from .base_matcher import BaseMatcher
from .semantic_matcher import SemanticMatcher
from .tfidf_matcher import TFIDFMatcher
from .tfidf_ml_matcher import TfidfMLMatcher
from .cross_encoder_matcher import CrossEncoderMatcher
from .llm_matcher import LLMMatcher

__all__ = [
    'Job',
    'MatchResult',
    'BaseMatcher',
    'SemanticMatcher',
    'TFIDFMatcher',
    'TfidfMLMatcher',
    'CrossEncoderMatcher',
    'LLMMatcher'
]
