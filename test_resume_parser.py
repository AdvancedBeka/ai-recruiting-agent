"""
Test script for resume parsing
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from resume_parser import TextExtractor, PDFParser, DOCXParser
from config import settings


def test_parsers():
    """Test individual parsers"""
    print("=" * 60)
    print("Testing Parsers")
    print("=" * 60)

    pdf_parser = PDFParser()
    docx_parser = DOCXParser()

    print(f"\n✓ PDF Parser initialized")
    print(f"  Supported extensions: {pdf_parser.supported_extensions}")

    print(f"\n✓ DOCX Parser initialized")
    print(f"  Supported extensions: {docx_parser.supported_extensions}")


def test_parse_resumes():
    """Test parsing resumes from storage"""
    print("\n" + "=" * 60)
    print("Parsing Resumes from Storage")
    print("=" * 60)

    resume_dir = settings.resume_storage_path

    if not resume_dir.exists():
        print(f"\n⚠ Resume directory not found: {resume_dir}")
        print("  Please run test_email.py first to download some resumes")
        return

    # Найдем все файлы резюме
    resume_files = []
    for ext in ['.pdf', '.docx', '.txt']:
        resume_files.extend(list(resume_dir.glob(f'*{ext}')))

    if not resume_files:
        print(f"\n⚠ No resume files found in {resume_dir}")
        print("  Please run test_email.py first to download some resumes")
        return

    print(f"\nFound {len(resume_files)} resume file(s)")

    # Парсим каждое резюме
    extractor = TextExtractor()
    parsed_resumes = []

    for i, resume_file in enumerate(resume_files[:5], 1):  # Парсим первые 5
        print(f"\n--- Resume {i}/{min(len(resume_files), 5)} ---")
        print(f"File: {resume_file.name}")

        try:
            resume = extractor.parse_resume(str(resume_file))

            if resume:
                print(f"✓ Parsed successfully")
                print(f"  Name: {resume.contact_info.name or 'N/A'}")
                print(f"  Email: {resume.contact_info.email or 'N/A'}")
                print(f"  Phone: {resume.contact_info.phone or 'N/A'}")
                print(f"  Skills found: {len(resume.skills)}")
                if resume.skills:
                    print(f"    Top skills: {', '.join(resume.skills[:5])}")
                print(f"  Keywords: {len(resume.keywords)}")
                if resume.keywords:
                    print(f"    Top keywords: {', '.join(resume.keywords[:5])}")
                print(f"  Text length: {len(resume.raw_text)} characters")

                parsed_resumes.append(resume)
            else:
                print(f"✗ Failed to parse")

        except Exception as e:
            print(f"✗ Error: {e}")

    return parsed_resumes


def save_parsed_resumes(resumes):
    """Save parsed resumes to JSON"""
    if not resumes:
        return

    print("\n" + "=" * 60)
    print("Saving Parsed Resumes")
    print("=" * 60)

    output_dir = Path("data/parsed_resumes")
    output_dir.mkdir(parents=True, exist_ok=True)

    for resume in resumes:
        output_file = output_dir / f"{Path(resume.file_name).stem}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(resume.to_json())

        print(f"✓ Saved: {output_file.name}")

    print(f"\nTotal: {len(resumes)} resume(s) saved to {output_dir}")


def demonstrate_features():
    """Demonstrate parser features with sample text"""
    print("\n" + "=" * 60)
    print("Demonstrating Parser Features")
    print("=" * 60)

    # Создаем пример резюме
    sample_resume = """
John Doe
Senior Python Developer

Email: john.doe@example.com
Phone: +1 (555) 123-4567
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe

SUMMARY
Experienced Python developer with 5+ years of expertise in backend development,
machine learning, and cloud technologies. Passionate about building scalable systems.

SKILLS
Python, Django, FastAPI, Flask, PostgreSQL, MongoDB, Redis, Docker, Kubernetes,
AWS, Git, Machine Learning, TensorFlow, PyTorch, React, JavaScript

EXPERIENCE
Senior Python Developer | Tech Company | 2020-2023
- Developed RESTful APIs using FastAPI
- Implemented machine learning models for recommendation system
- Optimized database queries improving performance by 40%

Python Developer | Startup Inc | 2018-2020
- Built microservices architecture
- Integrated third-party APIs
- Mentored junior developers
"""

    # Сохраняем во временный файл
    temp_file = Path("data/temp_resume.txt")
    temp_file.parent.mkdir(parents=True, exist_ok=True)

    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_resume)

    # Парсим
    extractor = TextExtractor()
    resume = extractor.parse_resume(str(temp_file))

    if resume:
        print("\n✓ Sample resume parsed successfully\n")

        print("Contact Info:")
        print(f"  Name: {resume.contact_info.name}")
        print(f"  Email: {resume.contact_info.email}")
        print(f"  Phone: {resume.contact_info.phone}")
        print(f"  LinkedIn: {resume.contact_info.linkedin}")
        print(f"  GitHub: {resume.contact_info.github}")

        print(f"\nSkills ({len(resume.skills)}):")
        for skill in resume.skills[:10]:
            print(f"  • {skill}")

        print(f"\nSummary:")
        if resume.summary:
            print(f"  {resume.summary[:200]}...")

        print(f"\nTop Keywords:")
        for keyword in resume.keywords[:10]:
            print(f"  • {keyword}")

        # Показываем JSON
        print(f"\nJSON representation (first 500 chars):")
        json_str = resume.to_json()
        print(json_str[:500] + "...")

    # Удаляем временный файл
    if temp_file.exists():
        temp_file.unlink()


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Resume Parser Test")
    print("=" * 60)

    try:
        # Test parsers
        test_parsers()

        # Demonstrate features
        demonstrate_features()

        # Parse real resumes if available
        parsed_resumes = test_parse_resumes()

        # Save results
        if parsed_resumes:
            save_parsed_resumes(parsed_resumes)

        print("\n" + "=" * 60)
        print("Testing Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
