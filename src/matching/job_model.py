"""
Job Model - модель вакансии для matching
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Job(BaseModel):
    """Модель вакансии"""

    # Основная информация
    job_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None

    # Описание
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None

    # Структурированные данные
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    education_level: Optional[str] = None

    # Дополнительная информация
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None  # full-time, part-time, contract
    remote_option: bool = False

    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    is_active: bool = True

    # Полный текст для matching (автогенерируется)
    full_text: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def __init__(self, **data):
        super().__init__(**data)
        # Генерируем full_text если не предоставлен
        if not self.full_text:
            self.full_text = self.generate_full_text()

    def generate_full_text(self) -> str:
        """Генерация полного текста вакансии для matching"""
        parts = [
            f"Job Title: {self.title}",
        ]

        if self.company:
            parts.append(f"Company: {self.company}")

        if self.location:
            parts.append(f"Location: {self.location}")

        parts.append(f"\nDescription:\n{self.description}")

        if self.requirements:
            parts.append(f"\nRequirements:\n{self.requirements}")

        if self.responsibilities:
            parts.append(f"\nResponsibilities:\n{self.responsibilities}")

        if self.required_skills:
            parts.append(f"\nRequired Skills: {', '.join(self.required_skills)}")

        if self.nice_to_have_skills:
            parts.append(f"\nNice to Have: {', '.join(self.nice_to_have_skills)}")

        if self.experience_years:
            parts.append(f"\nExperience: {self.experience_years}+ years")

        return "\n".join(parts)

    def to_dict(self):
        """Конвертация в словарь"""
        return self.model_dump()

    def to_json(self):
        """Конвертация в JSON"""
        return self.model_dump_json(indent=2)


class MatchResult(BaseModel):
    """Результат сопоставления резюме и вакансии"""

    # Идентификаторы
    resume_id: str  # file_name или ID резюме
    job_id: str

    # Scores
    overall_score: float = Field(ge=0.0, le=1.0)  # Общий score (0-1)
    skills_match: float = Field(default=0.0, ge=0.0, le=1.0)
    experience_match: float = Field(default=0.0, ge=0.0, le=1.0)
    semantic_similarity: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Детали
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)

    # Объяснение (особенно для LLM)
    explanation: Optional[str] = None

    # Метаданные
    matching_method: str  # "semantic", "tfidf", "llm"
    matched_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self):
        """Конвертация в словарь"""
        return self.model_dump()

    def to_json(self):
        """Конвертация в JSON"""
        return self.model_dump_json(indent=2)
