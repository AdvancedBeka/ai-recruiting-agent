"""
Demo: Comparing All Three Matching Approaches

Demonstrates:
1. Using MatcherComparison utility
2. Comparing results from all 3 matchers
3. Statistical analysis
4. Finding best matcher
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from matching import Job
from matching.matcher_comparison import MatcherComparison
from resume_parser import TextExtractor

print("\n" + "=" * 70)
print("Matcher Comparison Demo")
print("=" * 70)

# Step 1: Parse sample resume
print("\nStep 1: Parsing sample resume...")

extractor = TextExtractor(use_nlp=True)

sample_resume = """
Sarah Johnson
Full Stack Developer

Contact: sarah.johnson@email.com | +1-555-987-6543
LinkedIn: linkedin.com/in/sarahjohnson

SUMMARY
Full-stack developer with 5 years of experience building modern web applications.
Expertise in React, Node.js, TypeScript, and cloud technologies. Passionate about
creating scalable and maintainable solutions.

SKILLS
Frontend: React, TypeScript, JavaScript, HTML, CSS, Redux, Next.js
Backend: Node.js, Express, Python, FastAPI
Databases: PostgreSQL, MongoDB, Redis
DevOps: Docker, Kubernetes, AWS, CI/CD
Tools: Git, Jest, Webpack, Vite

EXPERIENCE
Senior Full Stack Developer | WebTech Solutions | 2021 - Present
- Led development of React-based SaaS platform serving 50K+ users
- Built RESTful APIs with Node.js and Express
- Implemented microservices architecture with Docker and Kubernetes
- Deployed applications on AWS (EC2, S3, RDS)
- Mentored 3 junior developers

Full Stack Developer | StartupCo | 2019 - 2021
- Developed e-commerce platform with React and Node.js
- Integrated payment systems and third-party APIs
- Optimized database queries (PostgreSQL)
- Implemented automated testing with Jest

EDUCATION
B.S. Computer Science | State University | 2019
"""

temp_resume = Path("data/temp_comparison_resume.txt")
temp_resume.parent.mkdir(parents=True, exist_ok=True)
temp_resume.write_text(sample_resume, encoding='utf-8')

resume = extractor.parse_resume(str(temp_resume))

if not resume:
    print("Failed to parse resume!")
    sys.exit(1)

print(f"✓ Parsed: {resume.contact_info.name}")
print(f"  Skills: {len(resume.skills)}")

# Step 2: Create sample jobs
print("\nStep 2: Creating sample jobs...")

jobs = [
    Job(
        job_id="job_001",
        title="Full Stack JavaScript Developer",
        company="Tech Startup",
        description="""
        Looking for Full Stack Developer with React and Node.js experience.
        Must have TypeScript, PostgreSQL, Docker skills.
        AWS experience is a plus.
        """,
        required_skills=["React", "Node.js", "TypeScript", "PostgreSQL", "Docker"],
        nice_to_have_skills=["AWS", "Kubernetes", "Redux"]
    ),
    Job(
        job_id="job_002",
        title="Python Backend Developer",
        company="Data Corp",
        description="""
        Python developer needed for backend services.
        Django or FastAPI experience required.
        Work with PostgreSQL and Redis.
        """,
        required_skills=["Python", "Django", "FastAPI", "PostgreSQL", "Redis"],
        nice_to_have_skills=["AWS", "Docker"]
    ),
    Job(
        job_id="job_003",
        title="Frontend React Developer",
        company="Design Agency",
        description="""
        React expert needed for UI development.
        TypeScript, HTML, CSS required.
        Next.js and modern tooling experience preferred.
        """,
        required_skills=["React", "TypeScript", "HTML", "CSS", "JavaScript"],
        nice_to_have_skills=["Next.js", "Redux", "Webpack", "Vite"]
    )
]

print(f"✓ Created {len(jobs)} sample jobs")

# Step 3: Initialize comparison utility
print("\nStep 3: Initializing matcher comparison...")

try:
    from config import Settings
    settings = Settings()
    api_key = settings.openai_api_key
except:
    api_key = None

comparison_tool = MatcherComparison(
    use_semantic=True,
    use_tfidf=True,
    use_llm=False,  # Set to True if you have OpenAI API key
    openai_api_key=api_key
)

print(f"✓ Initialized with {len(comparison_tool.matchers)} matchers")

# Step 4: Compare resume with each job
print("\n" + "=" * 70)
print("Step 4: Comparing Resume with Jobs")
print("=" * 70)

all_comparisons = []

for job in jobs:
    print(f"\n{'=' * 70}")
    print(f"Job: {job.title}")
    print(f"{'=' * 70}")

    comparison = comparison_tool.compare_single(resume, job)
    all_comparisons.append(comparison)

    # Print detailed comparison
    comparison_tool.print_comparison(comparison)

# Step 5: Overall statistics
print("\n" + "=" * 70)
print("Step 5: Overall Statistics")
print("=" * 70)

# Find best matcher
best_matcher_stats = comparison_tool.get_best_matcher(all_comparisons)

print("\n🏆 Matcher Performance:")
print(f"  Semantic (Sentence-BERT): {best_matcher_stats['semantic']} wins")
print(f"  TF-IDF: {best_matcher_stats['tfidf']} wins")
print(f"  LLM: {best_matcher_stats['llm']} wins")

# Correlations
correlations = comparison_tool.calculate_correlation(all_comparisons)

if correlations:
    print("\n📊 Correlation between matchers:")
    for pair, corr in correlations.items():
        print(f"  {pair}: {corr:.3f}")

# Best job match
print("\n🎯 Best Job Matches for Resume:")
sorted_comps = sorted(all_comparisons, key=lambda x: x.average_score, reverse=True)

for i, comp in enumerate(sorted_comps, 1):
    job = next(j for j in jobs if j.job_id == comp.job_id)
    print(f"  {i}. {job.title}: {comp.average_score:.1%} (agreement: {comp.agreement_level})")

# Step 6: Recommendations
print("\n" + "=" * 70)
print("Step 6: Recommendations")
print("=" * 70)

best_job = sorted_comps[0]
job = next(j for j in jobs if j.job_id == best_job.job_id)

print(f"\n✅ Best Match: {job.title}")
print(f"   Average Score: {best_job.average_score:.1%}")
print(f"   Agreement: {best_job.agreement_level}")

if best_job.semantic_result:
    print(f"\n📝 Skills to Highlight:")
    for skill in best_job.semantic_result.matched_skills[:8]:
        print(f"   • {skill}")

    if best_job.semantic_result.missing_skills:
        print(f"\n⚠ Skills to Acquire:")
        for skill in best_job.semantic_result.missing_skills[:5]:
            print(f"   • {skill}")

# Cleanup
if temp_resume.exists():
    temp_resume.unlink()

print("\n" + "=" * 70)
print("Demo Complete!")
print("=" * 70)

print("\n💡 Key Takeaways:")
print("  • Different matchers may give different scores")
print("  • Average score provides balanced view")
print("  • High agreement = all matchers agree on quality")
print("  • Low variance = consistent results across methods")

print()
