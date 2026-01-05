"""
Semantic Matcher using Sentence-BERT with optional FAISS acceleration.

- Multilingual model (default paraphrase-multilingual-MiniLM-L12-v2)
- Caches embeddings for reuse
- Optionally builds/loads a FAISS index for fast top-K retrieval
"""
import logging
from typing import List, Optional
import sys
from pathlib import Path

import numpy as np

from .base_matcher import BaseMatcher
from .job_model import Job, MatchResult

sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_parser.models import Resume  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .embedding_store import EmbeddingStore
try:
    from .faiss_index import FaissIndex
    FAISS_HELPERS_AVAILABLE = True
except Exception:
    FAISS_HELPERS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Semantic matching will use fallback.")


class SemanticMatcher(BaseMatcher):
    """
    Sentence-BERT matcher with optional FAISS index for retrieval.
    """

    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        super().__init__()
        self.name = "Semantic Matcher (Sentence-BERT)"
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None  # type: ignore
        self.store = EmbeddingStore(cache_path=Path("./data/cache/semantic_embeddings.pkl"))
        self.faiss_index: Optional[FaissIndex] = None

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading Sentence-BERT model: {model_name}")
                self.model = SentenceTransformer(model_name)
                if FAISS_HELPERS_AVAILABLE:
                    dim = self.model.get_sentence_embedding_dimension()
                    try:
                        self.faiss_index = FaissIndex(dim=dim, index_path=Path("./data/cache/faiss.index"))
                    except Exception as exc:
                        logger.warning(f"FAISS not initialized: {exc}")
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                self.model = None
        else:
            logger.warning("Sentence-transformers not installed. Using fallback method.")

    def match(self, resume: Resume, job: Job) -> MatchResult:
        # Skills overlap
        skills_score, matched_skills, missing_skills = self.calculate_skills_match(
            resume.skills,
            job.required_skills
        )

        semantic_score = self._calculate_semantic_similarity(resume, job)

        overall_score = (semantic_score * 0.6) + (skills_score * 0.4)

        return MatchResult(
            resume_id=resume.file_name,
            job_id=job.job_id,
            overall_score=overall_score,
            skills_match=skills_score,
            semantic_similarity=semantic_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matching_method="semantic",
            explanation=self._generate_explanation(
                overall_score,
                semantic_score,
                skills_score,
                matched_skills,
                missing_skills
            )
        )

    def _calculate_semantic_similarity(self, resume: Resume, job: Job) -> float:
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not self.model:
            return self._fallback_similarity(resume, job)

        try:
            resume_text = self._prepare_resume_text(resume)
            job_text = job.full_text

            resume_embedding = self.store.get_or_compute(resume.file_name, resume_text, self.model)
            job_key = f"job::{job.job_id}::{hash(job_text)}"
            job_embedding = self.store.get_or_compute(job_key, job_text, self.model)

            similarity = cosine_similarity([resume_embedding], [job_embedding])[0][0]
            normalized_similarity = (similarity + 1) / 2
            return float(normalized_similarity)
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return self._fallback_similarity(resume, job)

    def _prepare_resume_text(self, resume: Resume) -> str:
        parts = []
        if resume.contact_info.name:
            parts.append(f"Name: {resume.contact_info.name}")
        if resume.summary:
            parts.append(f"Summary: {resume.summary}")
        if resume.skills:
            parts.append(f"Skills: {', '.join(resume.skills)}")
        if resume.raw_text:
            parts.append(resume.raw_text[:500])
        return "\n\n".join(parts)

    def _fallback_similarity(self, resume: Resume, job: Job) -> float:
        resume_words = set(resume.keywords[:20]) | set(resume.skills)
        job_words = set(job.required_skills) | set(job.nice_to_have_skills)
        if not resume_words or not job_words:
            return 0.0
        intersection = len(resume_words.intersection(job_words))
        union = len(resume_words.union(job_words))
        return intersection / union if union > 0 else 0.0

    def _generate_explanation(
        self,
        overall_score: float,
        semantic_score: float,
        skills_score: float,
        matched_skills: List[str],
        missing_skills: List[str]
    ) -> str:
        lines = [
            f"Overall Match: {overall_score:.1%}",
            f"  - Semantic Similarity: {semantic_score:.1%}",
            f"  - Skills Match: {skills_score:.1%}",
            "",
        ]
        if matched_skills:
            lines.append(f"Matched Skills ({len(matched_skills)}):")
            lines.append(f"  {', '.join(matched_skills[:10])}")
            lines.append("")
        if missing_skills:
            lines.append(f"Missing Skills ({len(missing_skills)}):")
            lines.append(f"  {', '.join(missing_skills[:10])}")
        return "\n".join(lines)

    def match_many_optimized(
        self,
        resumes: List[Resume],
        job: Job,
        top_n: int = 5
    ) -> List[MatchResult]:
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not self.model:
            return self.match_many(resumes, job, top_n)

        try:
            # Build FAISS index if available and empty
            if self.faiss_index and self.faiss_index.index.ntotal == 0:
                self._build_faiss_index(resumes)

            candidate_resumes = resumes
            # Preselect via FAISS if index present
            if self.faiss_index and self.faiss_index.index.ntotal > 0:
                job_emb = self.model.encode([job.full_text])[0].astype(np.float32)
                top_hits = self.faiss_index.search(np.array([job_emb]), top_k=max(top_n * 3, 10))
                id_to_resume = {r.file_name: r for r in resumes}
                filtered = [id_to_resume[rid] for rid, _ in top_hits if rid in id_to_resume]
                if filtered:
                    candidate_resumes = filtered

            resume_texts = [self._prepare_resume_text(r) for r in candidate_resumes]
            logger.info(f"Encoding {len(resume_texts)} resumes (optimized)...")
            resume_embeddings = self.model.encode(resume_texts, show_progress_bar=False)
            job_embedding = self.model.encode([job.full_text])[0]

            similarities = cosine_similarity(resume_embeddings, [job_embedding])

            results = []
            for resume, similarity in zip(candidate_resumes, similarities):
                semantic_score = (similarity[0] + 1) / 2
                skills_score, matched_skills, missing_skills = self.calculate_skills_match(
                    resume.skills,
                    job.required_skills
                )
                overall_score = (semantic_score * 0.6) + (skills_score * 0.4)
                result = MatchResult(
                    resume_id=resume.file_name,
                    job_id=job.job_id,
                    overall_score=overall_score,
                    skills_match=skills_score,
                    semantic_similarity=semantic_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    matching_method="semantic_batch",
                    explanation=self._generate_explanation(
                        overall_score,
                        semantic_score,
                        skills_score,
                        matched_skills,
                        missing_skills
                    )
                )
                results.append(result)

            results.sort(key=lambda x: x.overall_score, reverse=True)
            return results[:top_n]

        except Exception as e:
            logger.error(f"Error in optimized matching: {e}")
            return self.match_many(resumes, job, top_n)

    def _build_faiss_index(self, resumes: List[Resume]):
        if not self.faiss_index or not self.model:
            return
        try:
            texts = [self._prepare_resume_text(r) for r in resumes]
            logger.info(f"Building FAISS index for {len(texts)} resumes...")
            embeddings = self.model.encode(texts, show_progress_bar=False)
            embeddings = np.array(embeddings, dtype=np.float32)
            self.faiss_index.add_embeddings(embeddings, [r.file_name for r in resumes])
            self.faiss_index.save()
        except Exception as exc:
            logger.error(f"Failed to build FAISS index: {exc}")

