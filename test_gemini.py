"""
Test script for Gemini Matcher

Tests Google Gemini 2.0 Flash via AI Studio for resume matching
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n" + "=" * 60)
print("Gemini Matcher Test (AI Studio)")
print("=" * 60)

# Check dependencies
print("\nChecking dependencies...")

try:
    import google.generativeai as genai
    print("✓ google-generativeai installed")
    GENAI_OK = True
except ImportError:
    print("✗ google-generativeai not installed")
    print("  Run: pip install google-generativeai")
    GENAI_OK = False

from matching import GeminiMatcher, Job
from resume_parser import TextExtractor
from config import Settings

print("\n" + "=" * 60)
print("Step 1: Load Configuration")
print("=" * 60)

settings = Settings()

if not settings.google_api_key:
    print("⚠ GOOGLE_API_KEY not configured in .env")
    print("\nTo use Gemini matcher:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Add to .env file:")
    print("   GOOGLE_API_KEY=your-api-key-here")
    print("\n✨ Note: AI Studio is FREE to use with generous limits!")
    sys.exit(1)

print(f"✓ Google API Key configured")

print("\n" + "=" * 60)
print("Step 2: Parse Sample Resume")
print("=" * 60)

extractor = TextExtractor(use_nlp=True)

sample_resume = """
Jane Smith
Senior Full Stack Developer

Email: jane.smith@email.com
Phone: +1-555-987-6543
LinkedIn: linkedin.com/in/janesmith

PROFESSIONAL SUMMARY
Experienced full-stack developer with 6 years of expertise in building scalable
web applications. Specialized in React, Node.js, TypeScript, and cloud technologies.
Strong background in microservices architecture and DevOps practices.

TECHNICAL SKILLS
Frontend: React, TypeScript, JavaScript, Next.js, Redux, HTML, CSS
Backend: Node.js, Express, Python, FastAPI, Django
Databases: PostgreSQL, MongoDB, Redis
DevOps: Docker, Kubernetes, AWS, CI/CD, Jenkins
Tools: Git, Jest, Webpack, Vite

WORK EXPERIENCE
Senior Full Stack Developer | Tech Solutions Inc | 2021 - Present
- Led development of React-based SaaS platform serving 100K+ users
- Built RESTful APIs and microservices with Node.js and Express
- Implemented CI/CD pipelines reducing deployment time by 60%
- Mentored team of 4 junior developers

Full Stack Developer | WebCo | 2018 - 2021
- Developed e-commerce platform with React and Node.js
- Optimized database queries improving performance by 40%
- Integrated payment systems and third-party APIs

EDUCATION
B.S. Computer Science | State University | 2018
GPA: 3.8/4.0
"""

temp_resume = Path("data/temp_gemini_resume.txt")
temp_resume.parent.mkdir(parents=True, exist_ok=True)
temp_resume.write_text(sample_resume, encoding='utf-8')

resume = extractor.parse_resume(str(temp_resume))

if not resume:
    print("✗ Failed to parse resume")
    sys.exit(1)

print(f"✓ Resume parsed: {resume.contact_info.name}")
print(f"  Skills: {len(resume.skills)}")
print(f"  Keywords: {len(resume.keywords)}")

print("\n" + "=" * 60)
print("Step 3: Create Sample Job")
print("=" * 60)

job = Job(
    job_id="job_001",
    title="Senior Full Stack JavaScript Developer",
    company="Innovative Startup",
    description="""
    We're looking for a Senior Full Stack Developer to join our fast-growing team.

    Responsibilities:
    - Build modern web applications with React and Node.js
    - Design and implement RESTful APIs
    - Work with PostgreSQL and MongoDB databases
    - Deploy and maintain applications on AWS
    - Collaborate with cross-functional teams

    Requirements:
    - 5+ years of experience with JavaScript/TypeScript
    - Strong proficiency in React and Node.js
    - Experience with PostgreSQL or MongoDB
    - Knowledge of Docker and Kubernetes
    - AWS cloud experience

    Nice to have:
    - Experience with Next.js
    - CI/CD pipeline experience
    - Microservices architecture knowledge
    """,
    required_skills=[
        "JavaScript", "TypeScript", "React", "Node.js", "Express",
        "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS"
    ],
    nice_to_have_skills=[
        "Next.js", "CI/CD", "Microservices", "Redux"
    ]
)

print(f"✓ Job created: {job.title}")
print(f"  Required skills: {len(job.required_skills)}")

print("\n" + "=" * 60)
print("Step 4: Test Gemini Matcher")
print("=" * 60)

if not GENAI_OK:
    print("✗ Cannot test - google-generativeai not installed")
    print("  Run: pip install google-generativeai")
    sys.exit(1)

try:
    print(f"\nInitializing Gemini matcher...")
    gemini_matcher = GeminiMatcher(
        api_key=settings.google_api_key,
        model_name="gemini-2.5-pro"
    )

    print(f"Matching resume with job using Gemini 2.5 Pro...")
    result = gemini_matcher.match(resume, job)

    print("\n" + "=" * 60)
    print("✓ Gemini Matching Complete!")
    print("=" * 60)

    print(f"\n📊 Results:")
    print(f"  Overall Score: {result.overall_score:.1%}")
    print(f"  Gemini Score: {result.semantic_similarity:.1%}")
    print(f"  Skills Match: {result.skills_match:.1%}")
    print(f"  Method: {result.matching_method}")

    print(f"\n✅ Matched Skills ({len(result.matched_skills)}):")
    for skill in result.matched_skills[:10]:
        print(f"    • {skill}")

    if result.missing_skills:
        print(f"\n⚠ Missing Skills ({len(result.missing_skills)}):")
        for skill in result.missing_skills[:5]:
            print(f"    • {skill}")

    if result.explanation:
        print(f"\n💡 Gemini Explanation:")
        print(f"  {result.explanation}")

    # Comparison with other matchers
    print("\n" + "=" * 60)
    print("Step 5: Compare with Other Matchers")
    print("=" * 60)

    from matching import SemanticMatcher, TFIDFMatcher

    print("\nRunning Semantic Matcher...")
    semantic = SemanticMatcher()
    sem_result = semantic.match(resume, job)

    print("Running TF-IDF Matcher...")
    tfidf = TFIDFMatcher()
    tfidf_result = tfidf.match(resume, job)

    print(f"\n{'Matcher':<20} {'Overall':<10} {'Semantic/LLM':<15} {'Skills':<10}")
    print("-" * 60)
    print(f"{'Gemini 2.5 Pro':<20} {result.overall_score:<10.1%} {result.semantic_similarity:<15.1%} {result.skills_match:<10.1%}")
    print(f"{'Sentence-BERT':<20} {sem_result.overall_score:<10.1%} {sem_result.semantic_similarity:<15.1%} {sem_result.skills_match:<10.1%}")
    print(f"{'TF-IDF':<20} {tfidf_result.overall_score:<10.1%} {tfidf_result.semantic_similarity:<15.1%} {tfidf_result.skills_match:<10.1%}")

    # Determine best
    scores = {
        'Gemini': result.overall_score,
        'Semantic': sem_result.overall_score,
        'TF-IDF': tfidf_result.overall_score
    }
    best = max(scores.items(), key=lambda x: x[1])
    print(f"\n🏆 Best Match: {best[0]} with {best[1]:.1%} score")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

    print("\n📝 Troubleshooting:")
    print("  1. Verify your API key is correct")
    print("  2. Check https://aistudio.google.com/app/apikey")
    print("  3. Make sure the API key has proper permissions")
    print("  4. Check if you've exceeded rate limits (unlikely with free tier)")

# Cleanup
if temp_resume.exists():
    temp_resume.unlink()

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)

print("\n💡 Gemini 2.5 Pro Benefits:")
print("  ✓ Most advanced Gemini model")
print("  ✓ 2M token context window (largest available)")
print("  ✓ Superior reasoning and understanding")
print("  ✓ Multimodal capabilities")
print("  ✓ Production-ready and stable")

print("\n📚 API Limits (Free Tier):")
print("  • 15 requests per minute")
print("  • 1,500 requests per day")
print("  • 1 million tokens per minute")

print()
