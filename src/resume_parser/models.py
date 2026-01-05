"""
Data models for resume parsing
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ContactInfo(BaseModel):
    """Контактная информация кандидата"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class WorkExperience(BaseModel):
    """Опыт работы"""
    position: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Образование"""
    degree: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None


class Resume(BaseModel):
    """Полная модель резюме"""

    # Метаданные файла
    file_path: str
    file_name: str
    file_type: str  # pdf, docx, etc.
    parsed_at: datetime = Field(default_factory=datetime.now)
    language: Optional[str] = "en"

    # Контактная информация
    contact_info: ContactInfo = Field(default_factory=ContactInfo)

    # Полный текст резюме
    raw_text: str = ""

    # Структурированные данные
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)

    # Дополнительная информация
    languages: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

    # Извлеченные ключевые слова
    keywords: List[str] = Field(default_factory=list)

    # Статус обработки
    parsing_errors: List[str] = Field(default_factory=list)
    is_valid: bool = True

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
