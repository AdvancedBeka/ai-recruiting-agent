"""
Cross-Encoder Matcher (zero-shot, no training).

Uses a pretrained cross-encoder from sentence-transformers to score
resume/job pairs directly. No fine-tuning required.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from .base_matcher import BaseMatcher
from .job_model import Job, MatchResult
import sys

# Make resume_parser importable
sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_parser.models import Resume

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import CrossEncoder

    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Cross-encoder matcher will fallback.")


class CrossEncoderMatcher(BaseMatcher):
    """
    Zero-shot matcher using a pretrained cross-encoder.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        super().__init__()
        self.name = "Cross-Encoder Matcher"
        self.model_name = model_name
        self.model: Optional[CrossEncoder] = None

        if ST_AVAILABLE:
            try:
                logger.info(f"Loading cross-encoder model: {model_name}")
                self.model = CrossEncoder(model_name)
            except Exception as exc:
                logger.error(f"Failed to load cross-encoder model: {exc}")
                self.model = None

    def match(self, resume: Resume, job: Job) -> MatchResult:
        """Compute match score via cross-encoder (or fallback)."""
        skills_score, matched_skills, missing_skills = self.calculate_skills_match(
            resume.skills, job.required_skills
        )

        ce_score = self._cross_encoder_score(resume, job)

        # Combine: 70% cross-encoder, 30% skills overlap
        overall = (ce_score * 0.7) + (skills_score * 0.3)

        return MatchResult(
            resume_id=resume.file_name,
            job_id=job.job_id,
            overall_score=float(overall),
            skills_match=float(skills_score),
            semantic_similarity=float(ce_score),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matching_method="cross_encoder",
            explanation=self._build_explanation(ce_score, skills_score, matched_skills, missing_skills),
        )

    def _cross_encoder_score(self, resume: Resume, job: Job) -> float:
        """Score pair using cross-encoder; fallback to simple heuristic."""
        if not self.model:
            return self._fallback_score(resume, job)

        resume_text = self._prepare_resume_text(resume)
        job_text = job.full_text

        try:
            score = self.model.predict([(resume_text, job_text)])[0]
            # Cross-encoder scores are roughly [0, 1] for this model
            score = float(max(0.0, min(1.0, score)))
            return score
        except Exception as exc:
            logger.error(f"Cross-encoder scoring failed: {exc}")
            return self._fallback_score(resume, job)

    def _fallback_score(self, resume: Resume, job: Job) -> float:
        """Lightweight overlap-based score as a fallback."""
        resume_words = set(resume.keywords[:30]) | set(resume.skills)
        job_words = set(job.required_skills) | set(job.nice_to_have_skills)

        if not resume_words or not job_words:
            return 0.0

        intersection = len(resume_words.intersection(job_words))
        union = len(resume_words.union(job_words))
        return intersection / union if union else 0.0

    def _prepare_resume_text(self, resume: Resume) -> str:
        parts: List[str] = []
        if resume.contact_info.name:
            parts.append(resume.contact_info.name)
        if resume.summary:
            parts.append(resume.summary)
        if resume.skills:
            parts.append(", ".join(resume.skills))
        if resume.raw_text:
            parts.append(resume.raw_text[:800])
        return "\n".join(parts)

    def _build_explanation(
        self,
        ce_score: float,
        skills_score: float,
        matched_skills: List[str],
        missing_skills: List[str],
    ) -> str:
        lines = [
            f"Cross-encoder score: {ce_score:.1%}",
            f"Skills overlap: {skills_score:.1%}",
        ]
        if matched_skills:
            lines.append(f"Matched: {', '.join(matched_skills[:8])}")
        if missing_skills:
            lines.append(f"Missing: {', '.join(missing_skills[:8])}")
        return "\n".join(lines)

