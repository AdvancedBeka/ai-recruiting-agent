"""
Quick zero-shot evaluation of matchers on synthetic data.

Runs available matchers (semantic, tfidf, cross_encoder, llm fallback)
on two resumes and one job to illustrate scoring differences.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from matching import SemanticMatcher, TFIDFMatcher, CrossEncoderMatcher, LLMMatcher, Job  # noqa: E402
from resume_parser.models import Resume  # noqa: E402


def make_resume(text: str, name: str) -> Resume:
    return Resume(
        file_path=name,
        file_name=name,
        file_type="txt",
        raw_text=text,
    )


def main():
    backend_resume = make_resume(
        "Python backend developer. FastAPI, PostgreSQL, Docker, AWS, microservices.", "backend.txt"
    )
    design_resume = make_resume(
        "Product designer, Figma, UX research, UI, prototyping, design systems.", "design.txt"
    )

    job = Job(
        job_id="job_demo",
        title="Senior Python Backend Engineer",
        description="Backend services with FastAPI, Docker, PostgreSQL on AWS.",
        required_skills=["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"],
        nice_to_have_skills=["Redis", "CI/CD"],
    )

    matchers = {
        "semantic": SemanticMatcher(),
        "tfidf": TFIDFMatcher(),
        "cross_encoder": CrossEncoderMatcher(),
        "llm_fallback": LLMMatcher(api_key=None),
    }

    resumes = [backend_resume, design_resume]

    print("\n=== Quick Eval ===")
    for name, matcher in matchers.items():
        print(f"\nMatcher: {name}")
        for res in resumes:
            try:
                result = matcher.match(res, job)
                print(
                    f"  {res.file_name:12} | overall={result.overall_score:.2f} "
                    f"sem/llm={result.semantic_similarity or 0:.2f} skills={result.skills_match:.2f}"
                )
            except Exception as exc:
                print(f"  {res.file_name:12} | failed: {exc}")


if __name__ == "__main__":
    main()
