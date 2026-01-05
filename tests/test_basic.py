"""
Basic tests for AI Recruiting Agent components
"""
import pytest
from pathlib import Path


def test_project_structure():
    """Test that project structure is correct"""
    project_root = Path(__file__).parent.parent

    # Check key directories exist
    assert (project_root / "src").exists()
    assert (project_root / "src" / "api").exists()
    assert (project_root / "src" / "matching").exists()
    assert (project_root / "src" / "resume_parser").exists()
    assert (project_root / "src" / "email_integration").exists()

    # Check key files exist
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "README.md").exists()
    assert (project_root / "docker-compose.yml").exists()


def test_imports():
    """Test that core modules can be imported"""
    try:
        from src.resume_parser import models
        from src.matching import base_matcher
        from src.api import app
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_resume_model():
    """Test Resume model creation"""
    from src.resume_parser.models import Resume, ContactInfo

    contact = ContactInfo(
        name="Test Candidate",
        email="test@example.com",
        phone="+1234567890"
    )

    resume = Resume(
        contact_info=contact,
        summary="Experienced software engineer",
        skills=["Python", "FastAPI", "Docker"],
        raw_text="Test resume content"
    )

    assert resume.contact_info.name == "Test Candidate"
    assert "Python" in resume.skills
    assert len(resume.skills) == 3


def test_job_model():
    """Test Job model creation"""
    from src.matching.job_model import Job

    job = Job(
        id="test-job-1",
        title="Senior Python Developer",
        description="We are looking for a senior Python developer",
        required_skills=["Python", "FastAPI", "Docker"],
        experience_years=5,
        location="Remote"
    )

    assert job.id == "test-job-1"
    assert job.title == "Senior Python Developer"
    assert "Python" in job.required_skills


def test_keyword_matcher():
    """Test keyword matcher basic functionality"""
    from src.matching.tfidf_matcher import TFIDFMatcher
    from src.matching.job_model import Job
    from src.resume_parser.models import Resume, ContactInfo

    matcher = TFIDFMatcher()

    # Create test job
    job = Job(
        id="test-job",
        title="Python Developer",
        description="Looking for Python developer with FastAPI experience",
        required_skills=["Python", "FastAPI", "REST API"],
        experience_years=3,
        location="Remote"
    )

    # Create test resume
    contact = ContactInfo(name="Test Dev", email="test@dev.com")
    resume = Resume(
        contact_info=contact,
        summary="Python developer with 5 years experience",
        skills=["Python", "FastAPI", "Docker", "PostgreSQL"],
        raw_text="Experienced Python developer. Built REST APIs with FastAPI."
    )

    # Test matching
    result = matcher.match(resume, job)

    assert result is not None
    assert 0.0 <= result.score <= 1.0
    assert result.algorithm == "keyword"


def test_api_models():
    """Test API Pydantic models"""
    from src.api.models import JobCreate, ResumeUpload

    # Test job creation model
    job_data = {
        "title": "Software Engineer",
        "description": "We need a great engineer",
        "required_skills": ["Python", "JavaScript"],
        "experience_years": 2,
        "location": "San Francisco"
    }

    job = JobCreate(**job_data)
    assert job.title == "Software Engineer"
    assert len(job.required_skills) == 2

    # Test resume upload model
    resume_data = {
        "filename": "resume.pdf",
        "content": "base64encodedcontent"
    }

    resume = ResumeUpload(**resume_data)
    assert resume.filename == "resume.pdf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
