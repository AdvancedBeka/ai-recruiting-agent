"""
Test script for NLP features

NOTE: Requires additional packages:
  pip install spacy scikit-learn nltk
  python -m spacy download en_core_web_sm
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n" + "=" * 60)
print("NLP Features Test")
print("=" * 60)

# Check if NLP packages are available
print("\nChecking NLP packages...")

try:
    import spacy
    print("✓ spaCy installed")
    SPACY_OK = True
except ImportError:
    print("✗ spaCy not installed")
    print("  Run: pip install spacy")
    print("  Then: python -m spacy download en_core_web_sm")
    SPACY_OK = False

try:
    import sklearn
    print("✓ scikit-learn installed")
    SKLEARN_OK = True
except ImportError:
    print("✗ scikit-learn not installed")
    print("  Run: pip install scikit-learn")
    SKLEARN_OK = False

try:
    import nltk
    print("✓ NLTK installed")
    NLTK_OK = True
except ImportError:
    print("✗ NLTK not installed")
    print("  Run: pip install nltk")
    NLTK_OK = False

if not (SPACY_OK and SKLEARN_OK):
    print("\n⚠ NLP packages not installed. Basic features will still work.")
    print("  To enable full NLP features, install the packages above.")

# Test NLP Processor
print("\n" + "=" * 60)
print("Testing NLP Processor")
print("=" * 60)

try:
    from resume_parser import NLPProcessor

    nlp = NLPProcessor(language='en')
    print("✓ NLP Processor initialized")

    # Sample text
    sample_text = """
    John Doe is a Senior Python Developer at Tech Company in New York.
    He has expertise in Python, JavaScript, React, Django, and PostgreSQL.
    John worked on machine learning projects using TensorFlow and PyTorch.
    He graduated from MIT in 2015 with a degree in Computer Science.
    Contact: john.doe@example.com | LinkedIn: linkedin.com/in/johndoe
    """

    # Test Named Entity Recognition
    print("\n--- Named Entity Recognition ---")
    entities = nlp.extract_entities(sample_text)
    for category, items in entities.items():
        if items:
            print(f"{category.capitalize()}: {', '.join(items[:5])}")

    # Test Skills Extraction
    print("\n--- Skills Extraction (NLP) ---")
    skills = nlp.extract_skills_nlp(sample_text)
    print(f"Found {len(skills)} skills:")
    for skill in skills[:15]:
        print(f"  • {skill}")

    # Test TF-IDF Keywords
    print("\n--- TF-IDF Keyword Extraction ---")
    keywords = nlp.extract_keywords_tfidf([sample_text], top_n=10)
    print(f"Top 10 keywords:")
    for word, score in keywords:
        print(f"  {word}: {score:.4f}")

    # Test Tokenization
    if NLTK_OK:
        print("\n--- Tokenization ---")
        tokens = nlp.tokenize(sample_text)
        print(f"Tokenized into {len(tokens)} tokens")
        print(f"First 10 tokens: {', '.join(tokens[:10])}")

    # Test Noun Phrases
    if SPACY_OK:
        print("\n--- Noun Phrases ---")
        noun_phrases = nlp.extract_noun_phrases(sample_text)
        print(f"Found {len(noun_phrases)} noun phrases:")
        for phrase in noun_phrases[:10]:
            print(f"  • {phrase}")

except ImportError as e:
    print(f"✗ Error importing NLP modules: {e}")
    print("  NLP features require: spacy, scikit-learn, nltk")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test TextExtractor with NLP
print("\n" + "=" * 60)
print("Testing TextExtractor with NLP")
print("=" * 60)

try:
    from resume_parser import TextExtractor

    # Test with NLP enabled
    print("\n--- With NLP enabled ---")
    extractor_nlp = TextExtractor(use_nlp=True)

    sample_resume = """
    Jane Smith
    Full Stack Developer

    Email: jane.smith@email.com
    Phone: +1-555-987-6543
    LinkedIn: linkedin.com/in/janesmith
    GitHub: github.com/janesmith

    SUMMARY
    Experienced full-stack developer with 7 years of expertise in building
    scalable web applications. Proficient in React, Node.js, and cloud technologies.

    SKILLS
    Frontend: React, TypeScript, HTML, CSS, Redux, Next.js
    Backend: Node.js, Python, FastAPI, Express, Django
    Database: PostgreSQL, MongoDB, Redis
    DevOps: Docker, Kubernetes, AWS, CI/CD, Jenkins
    """

    # Create temp file
    temp_file = Path("data/temp_nlp_test.txt")
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file.write_text(sample_resume, encoding='utf-8')

    # Parse with NLP
    resume = extractor_nlp.parse_resume(str(temp_file))

    if resume:
        print(f"✓ Resume parsed successfully")
        print(f"\nSkills ({len(resume.skills)}):")
        for skill in resume.skills[:15]:
            print(f"  • {skill}")

        print(f"\nKeywords ({len(resume.keywords)}):")
        for keyword in resume.keywords[:10]:
            print(f"  • {keyword}")

    # Test without NLP
    print("\n--- Without NLP (basic mode) ---")
    extractor_basic = TextExtractor(use_nlp=False)
    resume_basic = extractor_basic.parse_resume(str(temp_file))

    if resume_basic:
        print(f"✓ Resume parsed (basic mode)")
        print(f"\nSkills: {len(resume_basic.skills)}")
        print(f"Keywords: {len(resume_basic.keywords)}")

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)

print("\n📝 Summary:")
print(f"  spaCy: {'✓ Available' if SPACY_OK else '✗ Not installed'}")
print(f"  scikit-learn: {'✓ Available' if SKLEARN_OK else '✗ Not installed'}")
print(f"  NLTK: {'✓ Available' if NLTK_OK else '✗ Not installed'}")

if SPACY_OK and SKLEARN_OK:
    print("\n✓ All NLP features are available!")
else:
    print("\n⚠ Some NLP features are disabled. Install missing packages to enable.")
    print("\nTo install:")
    print("  pip install spacy scikit-learn nltk")
    print("  python -m spacy download en_core_web_sm")

print()
