"""
FAISS demo: build an index over resumes and query top-K for a job.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from matching import SemanticMatcher, Job  # noqa: E402
from resume_parser.models import Resume  # noqa: E402


def make_resume(text: str, name: str) -> Resume:
    return Resume(
        file_path=name,
        file_name=name,
        file_type="txt",
        raw_text=text,
    )


def main():
    matcher = SemanticMatcher()

    resumes = [
        make_resume("Python backend developer, FastAPI, PostgreSQL, Docker, AWS", "backend.txt"),
        make_resume("React front-end engineer, TypeScript, Next.js, UI/UX", "frontend.txt"),
        make_resume("Data scientist, NLP, transformers, PyTorch, ML", "datasci.txt"),
    ]

    job = Job(
        job_id="job_demo",
        title="Senior Python Backend Engineer",
        description="Backend services with FastAPI, PostgreSQL, Docker on AWS.",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        nice_to_have_skills=["Redis", "CI/CD"],
    )

    # Build FAISS index and search
    matcher._build_faiss_index(resumes)
    results = matcher.match_many_optimized(resumes, job, top_n=3)

    print("\nTop candidates (semantic + FAISS preselect):")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r.resume_id} | score={r.overall_score:.2f} | sem={r.semantic_similarity:.2f}")


if __name__ == "__main__":
    main()
