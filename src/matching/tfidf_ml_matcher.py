"""
TF-IDF + ML Matcher

Combines TF-IDF features of (resume, job) pairs with a lightweight
classifier (Logistic Regression) to predict match probability.

Features:
- Train on labeled pairs and optionally persist model to disk
- Predict probability for a resume/job pair
- Blends model probability with skills-overlap score for final ranking
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_matcher import BaseMatcher
from .job_model import Job, MatchResult
import sys

# Ensure resume_parser is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_parser.models import Resume

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    import joblib

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. TF-IDF ML matcher will be disabled.")


class TfidfMLMatcher(BaseMatcher):
    """
    Matcher using TF-IDF features + ML classifier.
    """

    def __init__(
        self,
        model_path: Path | str = Path("./data/models/tfidf_ml_model.joblib"),
        max_features: int = 5000,
    ):
        super().__init__()
        self.name = "TF-IDF + ML Matcher"
        self.model_path = Path(model_path)
        self.max_features = max_features
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.classifier: Optional[LogisticRegression] = None
        self.is_trained: bool = False

        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=(1, 2),
                stop_words="english",
                min_df=1,
            )
            self.classifier = LogisticRegression(
                max_iter=1000,
                n_jobs=None,
                class_weight="balanced",
            )
            self._maybe_load_model()

    def _maybe_load_model(self):
        """Load model from disk if present."""
        if not self.model_path.exists():
            return

        try:
            payload = joblib.load(self.model_path)
            self.vectorizer = payload["vectorizer"]
            self.classifier = payload["classifier"]
            self.is_trained = True
            logger.info(f"Loaded TF-IDF ML model from {self.model_path}")
        except Exception as exc:
            logger.error(f"Failed to load TF-IDF ML model: {exc}")

    def train(
        self,
        samples: List[Dict[str, Any]],
        save: bool = False,
    ):
        """
        Train classifier on labeled resume/job pairs.

        Each sample can be:
        - {"resume": Resume, "job": Job, "label": int}
        - {"resume_text": str, "job_text": str, "label": int}
        """
        if not SKLEARN_AVAILABLE or not self.vectorizer or not self.classifier:
            raise RuntimeError("scikit-learn not available; cannot train TF-IDF ML model.")

        texts = []
        labels = []

        for sample in samples:
            label = int(sample["label"])
            resume_text = self._extract_resume_text(sample)
            job_text = self._extract_job_text(sample)

            combined = self._combine_text(resume_text, job_text)
            texts.append(combined)
            labels.append(label)

        try:
            logger.info(f"Training TF-IDF vectorizer on {len(texts)} samples...")
            matrix = self.vectorizer.fit_transform(texts)
            logger.info("Fitting classifier...")
            self.classifier.fit(matrix, labels)
            self.is_trained = True

            if save:
                self._save_model()
        except Exception as exc:
            logger.error(f"Error training TF-IDF ML model: {exc}")
            raise

    def match(self, resume: Resume, job: Job) -> MatchResult:
        """Predict match probability and combine with skills overlap."""
        if not SKLEARN_AVAILABLE or not self.vectorizer or not self.classifier:
            raise RuntimeError("scikit-learn not available; cannot run TF-IDF ML matcher.")

        if not self.is_trained:
            raise RuntimeError(
                "TF-IDF ML model is not trained. Call train() or provide a saved model."
            )

        prob = self._predict_probability(resume, job)
        skills_score, matched_skills, missing_skills = self.calculate_skills_match(
            resume.skills,
            job.required_skills,
        )

        # Blend model probability with skills overlap
        overall = (prob * 0.6) + (skills_score * 0.4)

        return MatchResult(
            resume_id=resume.file_name,
            job_id=job.job_id,
            overall_score=float(overall),
            skills_match=float(skills_score),
            semantic_similarity=float(prob),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matching_method="tfidf_ml",
            explanation=self._build_explanation(prob, skills_score, matched_skills, missing_skills),
        )

    def _predict_probability(self, resume: Resume, job: Job) -> float:
        """Predict probability for a single resume/job pair."""
        combined = self._combine_text(
            self._get_resume_text(resume),
            job.full_text,
        )
        matrix = self.vectorizer.transform([combined])

        try:
            proba = self.classifier.predict_proba(matrix)[0][1]
        except Exception:
            # Fall back to decision_function if predict_proba not available
            decision = self.classifier.decision_function(matrix)[0]
            proba = 1 / (1 + pow(2.718281828, -decision))

        return float(max(0.0, min(1.0, proba)))

    def _combine_text(self, resume_text: str, job_text: str) -> str:
        """Create a combined text representation for TF-IDF."""
        return f"{resume_text}\n [SEP] \n{job_text}"

    def _extract_resume_text(self, sample: Dict[str, Any]) -> str:
        if "resume_text" in sample:
            return str(sample["resume_text"])
        resume: Resume = sample["resume"]
        return self._get_resume_text(resume)

    def _extract_job_text(self, sample: Dict[str, Any]) -> str:
        if "job_text" in sample:
            return str(sample["job_text"])
        job: Job = sample["job"]
        return job.full_text

    def _get_resume_text(self, resume: Resume) -> str:
        if resume.raw_text:
            return resume.raw_text
        if resume.summary:
            return resume.summary
        if resume.skills:
            return ", ".join(resume.skills)
        return resume.file_name

    def _build_explanation(
        self,
        prob: float,
        skills_score: float,
        matched_skills: List[str],
        missing_skills: List[str],
    ) -> str:
        lines = [
            f"Model probability: {prob:.1%}",
            f"Skills overlap: {skills_score:.1%}",
        ]

        if matched_skills:
            lines.append(f"Matched: {', '.join(matched_skills[:8])}")
        if missing_skills:
            lines.append(f"Missing: {', '.join(missing_skills[:8])}")

        return "\n".join(lines)

    def _save_model(self):
        """Persist vectorizer + classifier."""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(
                {"vectorizer": self.vectorizer, "classifier": self.classifier},
                self.model_path,
            )
            logger.info(f"Saved TF-IDF ML model to {self.model_path}")
        except Exception as exc:
            logger.error(f"Failed to save TF-IDF ML model: {exc}")
            raise

