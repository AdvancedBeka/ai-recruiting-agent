"""
TF-IDF Matcher with language-aware stop words (en/ru) and cosine similarity.
Zero training required.
"""
import logging
import re
import numpy as np
from typing import List
from .base_matcher import BaseMatcher
from .job_model import Job, MatchResult
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_parser.models import Resume  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. TF-IDF matching will use fallback.")


class TFIDFMatcher(BaseMatcher):
    """
    TF-IDF + cosine similarity matcher (no training).
    """

    def __init__(self, max_features: int = 500):
        super().__init__()
        self.name = "TF-IDF Matcher"
        self.max_features = max_features
        if not SKLEARN_AVAILABLE:
            logger.warning("Using fallback mode without sklearn")

    def match(self, resume: Resume, job: Job) -> MatchResult:
        skills_score, matched_skills, missing_skills = self.calculate_skills_match(
            resume.skills,
            job.required_skills
        )

        tfidf_score = self._calculate_tfidf_similarity(resume, job)
        overall_score = (tfidf_score * 0.5) + (skills_score * 0.5)

        return MatchResult(
            resume_id=resume.file_name,
            job_id=job.job_id,
            overall_score=overall_score,
            skills_match=skills_score,
            semantic_similarity=tfidf_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matching_method="tfidf",
            explanation=f"TF-IDF Similarity: {tfidf_score:.1%}\n"
                        f"Skills Match: {skills_score:.1%}\n"
                        f"Matched: {', '.join(matched_skills[:5])}\n"
                        f"Missing: {', '.join(missing_skills[:5])}"
        )

    def _calculate_tfidf_similarity(self, resume: Resume, job: Job) -> float:
        if not SKLEARN_AVAILABLE:
            return self._fallback_similarity(resume, job)

        try:
            resume_text = resume.raw_text if resume.raw_text else " ".join(resume.skills)
            job_text = job.full_text

            lang = self._detect_language(resume_text + job_text)
            vectorizer = self._build_vectorizer(lang)

            vectors = vectorizer.fit_transform([resume_text, job_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

            return float(max(0.0, min(1.0, similarity)))

        except Exception as e:
            logger.error(f"Error in TF-IDF calculation: {e}")
            return self._fallback_similarity(resume, job)

    def _fallback_similarity(self, resume: Resume, job: Job) -> float:
        resume_words = set(resume.keywords[:30]) | set(resume.skills)
        job_words = set(job.required_skills) | set(job.nice_to_have_skills)

        if not resume_words or not job_words:
            return 0.0

        intersection = len(resume_words.intersection(job_words))
        union = len(resume_words.union(job_words))

        return intersection / union if union > 0 else 0.0

    def _build_vectorizer(self, language: str):
        stop_words = 'english' if language == 'en' else None
        return TfidfVectorizer(
            max_features=self.max_features,
            stop_words=stop_words,
            ngram_range=(1, 2),
            min_df=1
        )

    def _detect_language(self, text: str) -> str:
        if re.search(r'[А-Яа-яЁё]', text):
            return "ru"
        return "en"

