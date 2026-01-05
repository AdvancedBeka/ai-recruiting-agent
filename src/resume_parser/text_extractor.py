"""
Text extractor for resumes across PDF, DOCX, and TXT with optional NLP helpers
and simple language detection (en/ru).
"""
import re
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .models import Resume, ContactInfo

try:
    from .nlp_processor import NLPProcessor
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    NLPProcessor = None  # type: ignore
    logger = logging.getLogger(__name__)
    logger.warning("NLP processor not available. Using basic extraction only.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextExtractor:
    """Extracts structured info from resume files."""

    def __init__(self, use_nlp: bool = True, language: str = "auto"):
        """
        Args:
            use_nlp: enable NLP helpers if available
            language: 'en', 'ru', or 'auto' to detect based on text
        """
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()

        self.requested_language = language
        self.use_nlp = use_nlp and NLP_AVAILABLE
        self.nlp_processor: Optional[NLPProcessor] = None

        if self.use_nlp and language != "auto":
            self._init_nlp(language)

        # Patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}')
        self.url_pattern = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)')

    def _init_nlp(self, language: str):
        try:
            self.nlp_processor = NLPProcessor(language=language)
            logger.info(f"NLP processor initialized (lang={language})")
        except Exception as e:
            logger.warning(f"Failed to initialize NLP processor: {e}")
            self.use_nlp = False
            self.nlp_processor = None

    def _detect_language(self, text: str) -> str:
        """Heuristic detection: ru if Cyrillic present, else en."""
        if re.search(r'[А-Яа-яЁё]', text):
            return "ru"
        return "en"

    def parse_resume(self, file_path: str) -> Optional[Resume]:
        """Parse resume file into structured Resume model."""
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        file_ext = path.suffix.lower()
        raw_text = None

        if file_ext == '.pdf':
            raw_text = self.pdf_parser.extract_text(file_path)
        elif file_ext == '.docx':
            raw_text = self.docx_parser.extract_text(file_path)
        elif file_ext == '.txt':
            raw_text = self._extract_from_txt(file_path)
        else:
            logger.error(f"Unsupported file type: {file_ext}")
            return None

        if not raw_text:
            logger.error(f"Failed to extract text from {file_path}")
            return None

        detected_lang = self.requested_language
        if self.requested_language == "auto":
            detected_lang = self._detect_language(raw_text)
            if self.use_nlp and (self.nlp_processor is None or getattr(self.nlp_processor, "language", "") != detected_lang):
                self._init_nlp(detected_lang)

        resume = Resume(
            file_path=str(path.absolute()),
            file_name=path.name,
            file_type=file_ext[1:],
            raw_text=raw_text,
            language=detected_lang,
        )

        resume.contact_info = self.extract_contact_info(raw_text)
        resume.skills = self.extract_skills(raw_text)
        resume.summary = self.extract_summary(raw_text)
        resume.keywords = self.extract_keywords(raw_text)

        logger.info(f"Successfully parsed resume: {path.name} (lang={detected_lang})")
        return resume

    def _extract_from_txt(self, file_path: str) -> Optional[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            for encoding in ['windows-1251', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
        return None

    def extract_contact_info(self, text: str) -> ContactInfo:
        contact_info = ContactInfo()

        emails = self.email_pattern.findall(text)
        if emails:
            contact_info.email = emails[0]

        phones = self.phone_pattern.findall(text)
        if phones:
            contact_info.phone = phones[0].strip()

        linkedin_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
        if linkedin_match:
            contact_info.linkedin = f"https://linkedin.com/in/{linkedin_match.group(1)}"

        github_match = re.search(r'github\.com/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
        if github_match:
            contact_info.github = f"https://github.com/{github_match.group(1)}"

        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) < 50 and not any(char.isdigit() for char in line):
                words = line.split()
                if 2 <= len(words) <= 4:
                    contact_info.name = line
                    break

        return contact_info

    def extract_skills(self, text: str) -> List[str]:
        if self.use_nlp and self.nlp_processor:
            try:
                skills = self.nlp_processor.extract_skills_nlp(text)
                logger.info(f"Extracted {len(skills)} skills using NLP")
                return skills[:30]
            except Exception as e:
                logger.warning(f"NLP skill extraction failed: {e}, falling back to basic method")

        skills: List[str] = []

        common_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'CI/CD',
            'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
            'TensorFlow', 'PyTorch', 'scikit-learn', 'Pandas', 'NumPy',
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum'
        ]

        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                skills.append(skill)

        skills_section = re.search(
            r'(?:skills?|навыки|technologies)[\s:]*(.{0,500}?)(?:\n\n|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if skills_section:
            skills_text = skills_section.group(1)
            found_skills = re.split(r'[,;\n]', skills_text)
            for skill in found_skills:
                skill = skill.strip()
                if skill and len(skill) < 50:
                    skills.append(skill)

        seen = set()
        unique_skills = []
        for skill in skills:
            low = skill.lower()
            if low not in seen:
                seen.add(low)
                unique_skills.append(skill)

        return unique_skills[:30]

    def extract_summary(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:summary|about|objective|profile|overview|резюме|о себе)[\s:]*(.{50,500}?)(?:\n\n|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                summary = re.sub(r'\s+', ' ', summary)
                return summary

        sentences = re.split(r'[.!?]\s+', text)
        if len(sentences) >= 2:
            summary = '. '.join(sentences[1:3])
            if 50 <= len(summary) <= 500:
                return summary

        return None

    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        if self.use_nlp and self.nlp_processor:
            try:
                keyword_scores = self.nlp_processor.extract_keywords_tfidf([text], top_n=top_n)
                keywords = [word for word, _ in keyword_scores]
                logger.info(f"Extracted {len(keywords)} keywords using TF-IDF")
                return keywords
            except Exception as e:
                logger.warning(f"TF-IDF keyword extraction failed: {e}, falling back to basic method")

        words = re.findall(r'\b[А-Яа-яA-Za-z]{4,}\b', text.lower())

        stop_words = {
            'have', 'been', 'were', 'with', 'from', 'this', 'that', 'these', 'those',
            'will', 'would', 'could', 'should',
            'или', 'или', 'это', 'также', 'ещё', 'есть', 'нет', 'года', 'год'
        }

        filtered = [w for w in words if w not in stop_words]

        freq: Dict[str, int] = {}
        for w in filtered:
            freq[w] = freq.get(w, 0) + 1

        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[^\w\s\n.,;:!?()\[\]{}@#$%&*+=\-/\\|<>"\']', '', text)
        return text.strip()

