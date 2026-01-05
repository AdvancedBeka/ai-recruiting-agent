"""
LLM Matcher hardened for reliability:
- Timeouts and retries
- Lightweight response cache
- Compact bilingual prompt (ru/en) with strict JSON output
"""
import logging
import json
import time
from typing import Optional, Tuple
from pathlib import Path
import sys

from .base_matcher import BaseMatcher
from .job_model import Job, MatchResult

sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_parser.models import Resume  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. LLM matching will use fallback.")

# Optional LangChain path
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except Exception:
    LANGCHAIN_AVAILABLE = False


class LLMMatcher(BaseMatcher):
    """
    Matcher using OpenAI GPT models with retries, timeout, and caching.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 15,
        max_retries: int = 2,
        use_langchain: bool = True,
    ):
        super().__init__()
        self.name = "LLM Matcher (GPT)"
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache = {}
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE

        if OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key, timeout=timeout, max_retries=max_retries)
                logger.info(f"LLM Matcher initialized with model: {model}")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("OpenAI not installed. Using fallback method.")

        self.lc_model = None
        self.lc_prompt = None
        if self.use_langchain:
            try:
                self.lc_model = ChatOpenAI(
                    model=self.model,
                    temperature=0.0,
                    timeout=timeout,
                    max_retries=max_retries,
                    openai_api_key=api_key,
                )
                self.lc_prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "You are a technical recruiter. Return ONLY JSON with fields score (0-1) and reason. Use ru if job is Russian else en.",
                        ),
                        ("user", "Job:\n{job_text}\n\nResume:\n{resume_text}"),
                    ]
                )
            except Exception as exc:
                logger.warning(f"LangChain initialization failed: {exc}")
                self.use_langchain = False

    def match(self, resume: Resume, job: Job) -> MatchResult:
        """Compute match using LLM, with fallback to skills."""
        skills_score, matched_skills, missing_skills = self.calculate_skills_match(
            resume.skills,
            job.required_skills,
        )

        if not OPENAI_AVAILABLE or not self.client:
            return self._fallback_match(resume, job, skills_score, matched_skills, missing_skills)

        try:
            result = self._llm_match(resume, job)
            overall_score = (result["score"] * 0.7) + (skills_score * 0.3)

            return MatchResult(
                resume_id=resume.file_name,
                job_id=job.job_id,
                overall_score=overall_score,
                skills_match=skills_score,
                experience_match=0.0,
                semantic_similarity=result["score"],
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                matching_method="llm",
                explanation=result["explanation"],
            )

        except Exception as e:
            logger.error(f"Error in LLM matching: {e}")
            return self._fallback_match(resume, job, skills_score, matched_skills, missing_skills)

    def _llm_match(self, resume: Resume, job: Job) -> dict:
        """LLM matching via OpenAI API with retries and cache."""
        cache_key = (resume.file_name, job.job_id, self.model)
        if cache_key in self.cache:
            return self.cache[cache_key]

        resume_text = self._prepare_resume_text(resume)
        job_text = job.full_text
        prompt = self._create_prompt(resume, job)
        last_exc = None

        # LangChain path
        if self.use_langchain and self.lc_model and self.lc_prompt:
            try:
                chain = self.lc_prompt | self.lc_model
                resp = chain.invoke({"job_text": job_text, "resume_text": resume_text})
                parsed = self._parse_llm_response(resp.content)
                self.cache[cache_key] = parsed
                return parsed
            except Exception as exc:
                logger.warning(f"LangChain LLM failed, falling back to raw client: {exc}")

        # Raw client path
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert technical recruiter. "
                                "Return only JSON with score 0..1 and brief reason."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                    max_tokens=400,
                    timeout=self.timeout,
                )

                content = response.choices[0].message.content
                logger.info(f"LLM response: {content}")
                parsed = self._parse_llm_response(content)
                self.cache[cache_key] = parsed
                return parsed

            except Exception as exc:
                last_exc = exc
                logger.warning(f"LLM attempt {attempt+1} failed: {exc}")
                time.sleep(1)

        logger.error(f"LLM matching failed after retries: {last_exc}")
        return {"score": 0.0, "explanation": "LLM failed; no score."}

    def _prepare_resume_text(self, resume: Resume) -> str:
        """Prepare resume text for LLM matching."""
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

    def _create_prompt(self, resume: Resume, job: Job) -> str:
        """Compact bilingual prompt."""
        candidate_info = f"""
Кандидат / Candidate:
Имя/Name: {resume.contact_info.name or 'N/A'}
Навыки/Skills: {', '.join(resume.skills[:15]) if resume.skills else 'N/A'}
Summary: {resume.summary[:200] if resume.summary else 'N/A'}
"""

        job_info = f"""
Вакансия / Job:
Title: {job.title}
Company: {job.company or 'N/A'}
Required Skills: {', '.join(job.required_skills) if job.required_skills else 'N/A'}
Description: {job.description[:400]}
"""

        prompt = f"""{candidate_info}

{job_info}

Задача / Task:
Оцени соответствие резюме вакансии. Дай число от 0 до 1 и короткое объяснение (ru/en по контексту).

Формат ответа / Response format (JSON only):
{{"score": 0.85, "reason": "..."}}"""

        return prompt

    def _parse_llm_response(self, content: str) -> dict:
        """Parse JSON response; clamp score to [0,1]."""
        logger.info(f"Parsing LLM response (length={len(content) if content else 0}): {repr(content[:200]) if content else 'None'}")

        if not content or not content.strip():
            logger.error("Empty LLM response received")
            return {"score": 0.0, "explanation": "Empty response from LLM"}

        # Remove markdown code blocks if present
        import re
        content_cleaned = content.strip()

        # Remove ```json and ``` markers
        if content_cleaned.startswith('```'):
            # Extract content between ``` markers
            match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content_cleaned, re.DOTALL)
            if match:
                content_cleaned = match.group(1).strip()

        try:
            result = json.loads(content_cleaned)
            score = float(result.get("score", 0.5))
            score = max(0.0, min(1.0, score))
            reasoning = result.get("reason") or result.get("reasoning") or "No explanation provided"
            logger.info(f"Successfully parsed LLM response: score={score}")
            return {"score": score, "explanation": reasoning}
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.error(f"Full content: {repr(content)}")

            score_match = re.search(r'"score":\s*([\d.]+)', content)
            score = float(score_match.group(1)) if score_match else 0.0
            return {"score": max(0.0, min(1.0, score)), "explanation": content[:200]}

    def _fallback_match(
        self,
        resume: Resume,
        job: Job,
        skills_score: float,
        matched_skills: list,
        missing_skills: list,
    ) -> MatchResult:
        """Fallback when LLM unavailable."""
        resume_words = set(resume.keywords[:20]) | set(resume.skills)
        job_words = set(job.required_skills) | set(job.nice_to_have_skills)

        keyword_score = 0.0
        if resume_words and job_words:
            inter = len(resume_words.intersection(job_words))
            union = len(resume_words.union(job_words))
            keyword_score = inter / union if union > 0 else 0.0

        overall_score = (keyword_score * 0.5) + (skills_score * 0.5)

        return MatchResult(
            resume_id=resume.file_name,
            job_id=job.job_id,
            overall_score=overall_score,
            skills_match=skills_score,
            semantic_similarity=keyword_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matching_method="llm_fallback",
            explanation=(
                "Fallback mode (LLM not available)\n"
                f"Skills match: {skills_score:.1%}\n"
                f"Keyword overlap: {keyword_score:.1%}"
            ),
        )
