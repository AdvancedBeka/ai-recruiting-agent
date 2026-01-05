"""
Configuration management using pydantic-settings
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Email Configuration (optional - only needed for email integration)
    email_host: str = "imap.gmail.com"
    email_port: int = 993
    email_address: Optional[str] = None
    email_password: Optional[str] = None

    # Storage Configuration
    resume_storage_path: Path = Path("./data/resumes")
    processed_emails_db: Path = Path("./data/processed_emails.json")

    # Email filters
    email_folder: str = "INBOX"
    email_subject_filter: Optional[str] = None

    # OpenAI Configuration (optional - only needed for OpenAI LLM matching)
    openai_api_key: Optional[str] = None

    # Google AI Studio Configuration (optional - for Gemini matching)
    google_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.resume_storage_path.mkdir(parents=True, exist_ok=True)
        self.processed_emails_db.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
