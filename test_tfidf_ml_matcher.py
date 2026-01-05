"""
Unit test for TF-IDF + ML matcher.

The test trains a tiny classifier on synthetic pairs and verifies that
matching returns scores in [0, 1] and ranks the positive pair higher
than an unrelated one.
"""
import sys
from pathlib import Path

# Make src importable
sys.path.insert(0, str(Path(__file__).parent / "src"))

from matching import TfidfMLMatcher, Job  # noqa: E402
from resume_parser.models import Resume  # noqa: E402


def make_resume(text: str, name: str = "resume.txt") -> Resume:
    return Resume(
        file_path=name,
        file_name=name,
        file_type="txt",
        raw_text=text,
    )


def test_tfidf_ml_matcher_ranks_positive_higher():
    matcher = TfidfMLMatcher(model_path=Path("data/models/test_tfidf_ml.joblib"))

    resume_good = make_resume(
        "Python backend developer with FastAPI, Docker, PostgreSQL, AWS experience."
    )
    resume_poor = make_resume(
        "Graphic designer focused on Figma, Adobe, UI/UX, branding, illustration."
    )

    job_backend = Job(
        job_id="job_backend",
        title="Senior Python Backend Engineer",
        description="Backend services with FastAPI, Docker, PostgreSQL on AWS.",
        required_skills=["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"],
        nice_to_have_skills=["Redis", "CI/CD"],
    )

    # Training samples: (resume, job, label)
    samples = [
        {"resume": resume_good, "job": job_backend, "label": 1},
        {"resume": resume_poor, "job": job_backend, "label": 0},
    ]

    matcher.train(samples, save=False)

    good_result = matcher.match(resume_good, job_backend)
    poor_result = matcher.match(resume_poor, job_backend)

    assert 0.0 <= good_result.overall_score <= 1.0
    assert 0.0 <= poor_result.overall_score <= 1.0
    assert good_result.overall_score > poor_result.overall_score

