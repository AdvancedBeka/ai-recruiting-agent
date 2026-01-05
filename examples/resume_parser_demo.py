"""
Example: Resume Parser Usage

Демонстрация возможностей парсера резюме
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resume_parser import TextExtractor, PDFParser, DOCXParser, Resume


def example_1_parse_pdf():
    """Пример 1: Парсинг PDF резюме"""
    print("\n" + "=" * 60)
    print("Example 1: Parse PDF Resume")
    print("=" * 60)

    pdf_parser = PDFParser()

    # Пример пути к PDF файлу
    pdf_file = "data/resumes/sample_resume.pdf"

    if Path(pdf_file).exists():
        # Извлечение текста
        text = pdf_parser.extract_text(pdf_file)
        if text:
            print(f"✓ Extracted {len(text)} characters")
            print(f"\nFirst 200 characters:")
            print(text[:200])

        # Метаданные
        metadata = pdf_parser.get_metadata(pdf_file)
        print(f"\nMetadata:")
        print(f"  Pages: {metadata['num_pages']}")
        print(f"  Author: {metadata.get('author', 'N/A')}")
    else:
        print(f"⚠ File not found: {pdf_file}")


def example_2_parse_docx():
    """Пример 2: Парсинг DOCX резюме"""
    print("\n" + "=" * 60)
    print("Example 2: Parse DOCX Resume")
    print("=" * 60)

    docx_parser = DOCXParser()

    # Пример пути к DOCX файлу
    docx_file = "data/resumes/sample_resume.docx"

    if Path(docx_file).exists():
        # Извлечение текста
        text = docx_parser.extract_text(docx_file)
        if text:
            print(f"✓ Extracted {len(text)} characters")

        # Параграфы
        paragraphs = docx_parser.extract_paragraphs(docx_file)
        print(f"\nFound {len(paragraphs)} paragraphs")

        # Метаданные
        metadata = docx_parser.get_metadata(docx_file)
        print(f"\nMetadata:")
        print(f"  Paragraphs: {metadata['num_paragraphs']}")
        print(f"  Tables: {metadata['num_tables']}")
    else:
        print(f"⚠ File not found: {docx_file}")


def example_3_full_parsing():
    """Пример 3: Полный парсинг с извлечением данных"""
    print("\n" + "=" * 60)
    print("Example 3: Full Resume Parsing")
    print("=" * 60)

    extractor = TextExtractor()

    # Создаем тестовое резюме
    sample_text = """
Jane Smith
Full Stack Developer

Contact: jane.smith@email.com | +1-555-987-6543
LinkedIn: linkedin.com/in/janesmith

Professional Summary
Passionate full-stack developer with 7 years of experience building web applications.
Expert in React, Node.js, and cloud technologies.

Technical Skills
Frontend: React, TypeScript, HTML, CSS, Redux
Backend: Node.js, Python, FastAPI, Express
Database: PostgreSQL, MongoDB, Redis
DevOps: Docker, Kubernetes, AWS, CI/CD
"""

    # Сохраняем во временный файл
    temp_file = Path("data/temp_demo.txt")
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file.write_text(sample_text, encoding='utf-8')

    # Парсим
    resume = extractor.parse_resume(str(temp_file))

    if resume:
        print("\n✓ Resume parsed successfully\n")

        print("=" * 40)
        print("CONTACT INFORMATION")
        print("=" * 40)
        print(f"Name: {resume.contact_info.name}")
        print(f"Email: {resume.contact_info.email}")
        print(f"Phone: {resume.contact_info.phone}")
        print(f"LinkedIn: {resume.contact_info.linkedin}")

        print(f"\n" + "=" * 40)
        print(f"SKILLS ({len(resume.skills)})")
        print("=" * 40)
        for skill in resume.skills:
            print(f"  • {skill}")

        print(f"\n" + "=" * 40)
        print("SUMMARY")
        print("=" * 40)
        print(resume.summary)

        print(f"\n" + "=" * 40)
        print(f"KEYWORDS ({len(resume.keywords)})")
        print("=" * 40)
        for keyword in resume.keywords[:15]:
            print(f"  • {keyword}")

        print(f"\n" + "=" * 40)
        print("RESUME OBJECT")
        print("=" * 40)
        print(f"File: {resume.file_name}")
        print(f"Type: {resume.file_type}")
        print(f"Parsed at: {resume.parsed_at}")
        print(f"Text length: {len(resume.raw_text)} chars")

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()


def example_4_extract_contact_info():
    """Пример 4: Извлечение контактной информации"""
    print("\n" + "=" * 60)
    print("Example 4: Extract Contact Information")
    print("=" * 60)

    extractor = TextExtractor()

    test_texts = [
        "John Doe\nemail: john@example.com\nphone: +1-555-123-4567",
        "Contact me: jane.smith@company.org or call (555) 987-6543",
        "GitHub: github.com/developer\nLinkedIn: linkedin.com/in/developer"
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"Text: {text[:50]}...")

        contact_info = extractor.extract_contact_info(text)
        print(f"Result:")
        print(f"  Email: {contact_info.email}")
        print(f"  Phone: {contact_info.phone}")
        print(f"  GitHub: {contact_info.github}")
        print(f"  LinkedIn: {contact_info.linkedin}")


def example_5_extract_skills():
    """Пример 5: Извлечение навыков"""
    print("\n" + "=" * 60)
    print("Example 5: Extract Skills")
    print("=" * 60)

    extractor = TextExtractor()

    sample_text = """
I am proficient in Python, JavaScript, and Go. I have experience with
React, Vue, and Angular frameworks. I work with PostgreSQL, MongoDB,
and Redis databases. I use Docker and Kubernetes for deployment.
"""

    skills = extractor.extract_skills(sample_text)

    print(f"\nFound {len(skills)} skills:")
    for skill in skills:
        print(f"  • {skill}")


def example_6_batch_processing():
    """Пример 6: Пакетная обработка резюме"""
    print("\n" + "=" * 60)
    print("Example 6: Batch Resume Processing")
    print("=" * 60)

    extractor = TextExtractor()
    resume_dir = Path("data/resumes")

    if not resume_dir.exists():
        print(f"⚠ Directory not found: {resume_dir}")
        print("  Run test_email.py first to download resumes")
        return

    # Находим все файлы резюме
    resume_files = []
    for ext in ['.pdf', '.docx', '.txt']:
        resume_files.extend(list(resume_dir.glob(f'*{ext}')))

    if not resume_files:
        print(f"⚠ No resume files found in {resume_dir}")
        return

    print(f"\nProcessing {len(resume_files)} resume(s)...")

    # Статистика
    stats = {
        'total': len(resume_files),
        'parsed': 0,
        'failed': 0,
        'avg_skills': 0,
        'avg_keywords': 0
    }

    parsed_resumes = []

    for resume_file in resume_files:
        try:
            resume = extractor.parse_resume(str(resume_file))
            if resume:
                stats['parsed'] += 1
                stats['avg_skills'] += len(resume.skills)
                stats['avg_keywords'] += len(resume.keywords)
                parsed_resumes.append(resume)
            else:
                stats['failed'] += 1
        except Exception as e:
            print(f"✗ Error processing {resume_file.name}: {e}")
            stats['failed'] += 1

    # Вычисляем средние значения
    if stats['parsed'] > 0:
        stats['avg_skills'] = stats['avg_skills'] / stats['parsed']
        stats['avg_keywords'] = stats['avg_keywords'] / stats['parsed']

    # Выводим статистику
    print(f"\n" + "=" * 40)
    print("PROCESSING STATISTICS")
    print("=" * 40)
    print(f"Total files: {stats['total']}")
    print(f"Successfully parsed: {stats['parsed']}")
    print(f"Failed: {stats['failed']}")
    print(f"Average skills per resume: {stats['avg_skills']:.1f}")
    print(f"Average keywords per resume: {stats['avg_keywords']:.1f}")

    # Топ навыки
    if parsed_resumes:
        all_skills = []
        for resume in parsed_resumes:
            all_skills.extend(resume.skills)

        skill_freq = {}
        for skill in all_skills:
            skill_freq[skill] = skill_freq.get(skill, 0) + 1

        top_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        print(f"\n" + "=" * 40)
        print("TOP 10 SKILLS ACROSS ALL RESUMES")
        print("=" * 40)
        for skill, count in top_skills:
            print(f"  {skill}: {count}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print(" " * 20 + "RESUME PARSER EXAMPLES")
    print("=" * 70)

    examples = [
        ("Parse PDF Resume", example_1_parse_pdf),
        ("Parse DOCX Resume", example_2_parse_docx),
        ("Full Resume Parsing", example_3_full_parsing),
        ("Extract Contact Info", example_4_extract_contact_info),
        ("Extract Skills", example_5_extract_skills),
        ("Batch Processing", example_6_batch_processing),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n" + "-" * 70)

    # Run all examples
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
