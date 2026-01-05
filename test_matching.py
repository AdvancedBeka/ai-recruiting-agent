"""
Test script for all three matching approaches

Tests:
1. Semantic Matcher (Sentence-BERT)
2. TF-IDF Matcher
3. LLM Matcher (OpenAI)

Compares results and demonstrates usage
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n" + "=" * 60)
print("Matching Engine Test - All 3 Approaches")
print("=" * 60)

# Check available packages
print("\nChecking dependencies...")

try:
    import sentence_transformers
    print("✓ sentence-transformers installed (for Semantic Matcher)")
    SBERT_OK = True
except ImportError:
    print("✗ sentence-transformers not installed")
    print("  Run: pip install sentence-transformers")
    SBERT_OK = False

try:
    import sklearn
    print("✓ scikit-learn installed (for TF-IDF Matcher)")
    SKLEARN_OK = True
except ImportError:
    print("✗ scikit-learn not installed")
    print("  Run: pip install scikit-learn")
    SKLEARN_OK = False

try:
    import openai
    print("✓ openai installed (for LLM Matcher)")
    OPENAI_OK = True
except ImportError:
    print("✗ openai not installed")
    print("  Run: pip install openai")
    OPENAI_OK = False

# Import our modules
from matching import SemanticMatcher, TFIDFMatcher, LLMMatcher, Job
from resume_parser import TextExtractor

print("\n" + "=" * 60)
print("Step 1: Parse Sample Resume")
print("=" * 60)

# Parse a sample resume
extractor = TextExtractor(use_nlp=True)

# Create temp sample resume
sample_resume_text = """
John Smith
Senior Python Developer

Email: john.smith@email.com
Phone: +1-555-123-4567
LinkedIn: linkedin.com/in/johnsmith
GitHub: github.com/johnsmith

PROFESSIONAL SUMMARY
Experienced Python developer with 7 years of expertise in building scalable
backend systems. Specialized in Django, FastAPI, and microservices architecture.
Strong background in AWS cloud services and Docker containerization.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, Bash
Frameworks: Django, FastAPI, Flask, React
Databases: PostgreSQL, MySQL, Redis, MongoDB
DevOps: Docker, Kubernetes, Jenkins, GitLab CI
Cloud: AWS (EC2, S3, Lambda, RDS), Azure
Tools: Git, JIRA, Confluence

WORK EXPERIENCE
Senior Python Developer | Tech Company | 2020 - Present
- Designed and implemented microservices architecture serving 1M+ users
- Built RESTful APIs using Django REST Framework and FastAPI
- Optimized PostgreSQL queries, reducing response time by 40%
- Implemented CI/CD pipelines with Jenkins and Docker
- Mentored junior developers and conducted code reviews

Python Developer | Software Inc | 2017 - 2020
- Developed backend services for e-commerce platform
- Integrated payment gateways and third-party APIs
- Worked with Redis for caching and session management
- Implemented automated testing with pytest

EDUCATION
B.S. Computer Science | University of Technology | 2017

PROJECTS
- Open-source contributor to Django and FastAPI
- Built ML-powered recommendation system using scikit-learn
- Created developer tools published on PyPI
"""

temp_resume = Path("data/temp_test_resume.txt")
temp_resume.parent.mkdir(parents=True, exist_ok=True)
temp_resume.write_text(sample_resume_text, encoding='utf-8')

resume = extractor.parse_resume(str(temp_resume))

if resume:
    print(f"✓ Resume parsed successfully")
    print(f"  Name: {resume.contact_info.name}")
    print(f"  Skills ({len(resume.skills)}): {', '.join(resume.skills[:10])}...")
    print(f"  Keywords ({len(resume.keywords)}): {', '.join(resume.keywords[:8])}...")
else:
    print("✗ Failed to parse resume")
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 2: Create Sample Job")
print("=" * 60)

job = Job(
    job_id="job_001",
    title="Senior Python Backend Developer",
    company="Tech Corp",
    description="""
    We are looking for an experienced Python Backend Developer to join our team.

    Responsibilities:
    - Design and develop scalable backend services using Python and Django
    - Build RESTful APIs and microservices
    - Work with PostgreSQL and Redis databases
    - Implement CI/CD pipelines
    - Deploy on AWS infrastructure

    Requirements:
    - 5+ years of experience with Python
    - Strong knowledge of Django or FastAPI
    - Experience with PostgreSQL, Redis
    - Understanding of Docker and Kubernetes
    - Experience with AWS cloud services
    """,
    required_skills=[
        "Python", "Django", "FastAPI", "PostgreSQL", "Redis",
        "Docker", "Kubernetes", "AWS", "REST API", "Microservices"
    ],
    nice_to_have_skills=[
        "Machine Learning", "GraphQL", "CI/CD", "Jenkins"
    ]
)

print(f"✓ Job created: {job.title}")
print(f"  Required skills ({len(job.required_skills)}): {', '.join(job.required_skills[:5])}...")

print("\n" + "=" * 60)
print("Step 3: Test Matching Approaches")
print("=" * 60)

results = {}

# Test 1: Semantic Matcher
print("\n--- Approach 1: Semantic Matcher (Sentence-BERT) ---")
try:
    semantic_matcher = SemanticMatcher()
    result = semantic_matcher.match(resume, job)
    results['semantic'] = result

    print(f"✓ Semantic matching complete")
    print(f"  Overall Score: {result.overall_score:.1%}")
    print(f"  Semantic Similarity: {result.semantic_similarity:.1%}")
    print(f"  Skills Match: {result.skills_match:.1%}")
    print(f"  Matched Skills ({len(result.matched_skills)}): {', '.join(result.matched_skills[:5])}")
    print(f"  Missing Skills ({len(result.missing_skills)}): {', '.join(result.missing_skills[:5])}")
except Exception as e:
    print(f"✗ Semantic matching failed: {e}")
    if not SBERT_OK:
        print("  Install sentence-transformers: pip install sentence-transformers")

# Test 2: TF-IDF Matcher
print("\n--- Approach 2: TF-IDF Matcher ---")
try:
    tfidf_matcher = TFIDFMatcher(max_features=500)
    result = tfidf_matcher.match(resume, job)
    results['tfidf'] = result

    print(f"✓ TF-IDF matching complete")
    print(f"  Overall Score: {result.overall_score:.1%}")
    print(f"  TF-IDF Similarity: {result.semantic_similarity:.1%}")
    print(f"  Skills Match: {result.skills_match:.1%}")
    print(f"  Explanation: {result.explanation[:100]}...")
except Exception as e:
    print(f"✗ TF-IDF matching failed: {e}")
    if not SKLEARN_OK:
        print("  Install scikit-learn: pip install scikit-learn")

# Test 3: LLM Matcher
print("\n--- Approach 3: LLM Matcher (OpenAI) ---")
try:
    from config import Settings
    settings = Settings()

    if settings.openai_api_key:
        llm_matcher = LLMMatcher(api_key=settings.openai_api_key, model="gpt-4o")
        result = llm_matcher.match(resume, job)
        results['llm'] = result

        if result.matching_method == "llm_fallback":
            print(f"⚠ LLM fallback mode (API quota exceeded or error)")
            print(f"  Overall Score: {result.overall_score:.1%}")
            print(f"  Skills Match: {result.skills_match:.1%}")
            print(f"  Note: Using keyword-based matching instead of GPT-4o")
        else:
            print(f"✓ LLM matching complete (GPT-4o)")
            print(f"  Overall Score: {result.overall_score:.1%}")
            print(f"  LLM Score: {result.semantic_similarity:.1%}")
            print(f"  Skills Match: {result.skills_match:.1%}")
            if result.explanation:
                print(f"  Explanation: {result.explanation[:150]}...")
    else:
        print("⚠ OpenAI API key not configured")
        print("  Set OPENAI_API_KEY in .env file to test LLM matching")
        # Test fallback
        llm_matcher = LLMMatcher()
        result = llm_matcher.match(resume, job)
        results['llm'] = result
        print(f"✓ Using fallback mode")
        print(f"  Overall Score: {result.overall_score:.1%}")
except Exception as e:
    print(f"✗ LLM matching failed: {e}")
    if not OPENAI_OK:
        print("  Install openai: pip install openai")

# Comparison
print("\n" + "=" * 60)
print("Step 4: Comparison of Results")
print("=" * 60)

if results:
    print("\nOverall Scores Comparison:")
    print(f"{'Method':<20} {'Overall':<10} {'Semantic/LLM':<15} {'Skills':<10}")
    print("-" * 60)

    for method, result in results.items():
        method_name = {
            'semantic': 'Sentence-BERT',
            'tfidf': 'TF-IDF',
            'llm': 'LLM (GPT)'
        }[method]

        sem_score = result.semantic_similarity if result.semantic_similarity else 0.0
        print(f"{method_name:<20} {result.overall_score:<10.1%} {sem_score:<15.1%} {result.skills_match:<10.1%}")

    # Find best match
    best_method = max(results.items(), key=lambda x: x[1].overall_score)
    print(f"\n🏆 Best Match: {best_method[0].upper()} with {best_method[1].overall_score:.1%} score")

    # Skills analysis
    print("\n📊 Skills Analysis:")
    if 'semantic' in results:
        r = results['semantic']
        print(f"  Matched: {len(r.matched_skills)}/{len(job.required_skills)} required skills")
        print(f"  Missing: {', '.join(r.missing_skills[:5])}")

# Test batch matching
print("\n" + "=" * 60)
print("Step 5: Batch Matching Test")
print("=" * 60)

if SBERT_OK:
    print("\nTesting optimized batch matching with SemanticMatcher...")

    # Create 3 resumes (same resume duplicated for demo)
    resumes = [resume, resume, resume]

    try:
        semantic_matcher = SemanticMatcher()
        batch_results = semantic_matcher.match_many_optimized(resumes, job, top_n=3)

        print(f"✓ Batch matching complete")
        print(f"  Processed {len(resumes)} resumes")
        print(f"  Top {len(batch_results)} results:")

        for i, result in enumerate(batch_results, 1):
            print(f"    {i}. {result.resume_id}: {result.overall_score:.1%}")
    except Exception as e:
        print(f"✗ Batch matching failed: {e}")
else:
    print("⚠ Batch matching requires sentence-transformers")

# Cleanup
if temp_resume.exists():
    temp_resume.unlink()

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)

print("\n📝 Summary:")
print(f"  Semantic Matcher: {'✓ Available' if SBERT_OK else '✗ Not available'}")
print(f"  TF-IDF Matcher: {'✓ Available' if SKLEARN_OK else '✗ Not available'}")
print(f"  LLM Matcher: {'✓ Available' if OPENAI_OK else '✗ Not available'}")

if not all([SBERT_OK, SKLEARN_OK, OPENAI_OK]):
    print("\n⚠ Some matchers are using fallback mode.")
    print("  Install missing packages for full functionality:")
    if not SBERT_OK:
        print("    pip install sentence-transformers")
    if not SKLEARN_OK:
        print("    pip install scikit-learn")
    if not OPENAI_OK:
        print("    pip install openai")

print()
