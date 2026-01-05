"""
NLP Processor для продвинутой обработки текста резюме

Использует:
- spaCy для NER (Named Entity Recognition)
- scikit-learn для TF-IDF
- NLTK для токенизации
"""
import logging
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Опциональные импорты NLP библиотек
try:
    import spacy
    from spacy.lang.en import English
    from spacy.lang.ru import Russian
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not installed. NER features will be limited.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed. TF-IDF features will be limited.")

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK not installed. Advanced tokenization will be limited.")


class NLPProcessor:
    """
    NLP процессор для извлечения информации из текста резюме
    """

    def __init__(self, language: str = 'en'):
        """
        Инициализация NLP процессора

        Args:
            language: Язык текста ('en' или 'ru')
        """
        self.language = language
        self.nlp = None

        # Загрузка spaCy модели
        if SPACY_AVAILABLE:
            self._load_spacy_model()

        # Инициализация NLTK
        if NLTK_AVAILABLE:
            self._init_nltk()

    def _load_spacy_model(self):
        """Загрузка spaCy модели"""
        try:
            if self.language == 'en':
                # Попытка загрузить английскую модель
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.info("Loaded spaCy model: en_core_web_sm")
                except OSError:
                    logger.warning("spaCy model 'en_core_web_sm' not found. Using blank English model.")
                    self.nlp = English()
            elif self.language == 'ru':
                try:
                    self.nlp = spacy.load("ru_core_news_sm")
                    logger.info("Loaded spaCy model: ru_core_news_sm")
                except OSError:
                    logger.warning("spaCy model 'ru_core_news_sm' not found. Using blank Russian model.")
                    self.nlp = Russian()
            else:
                logger.warning(f"Unsupported language: {self.language}. Using English.")
                self.nlp = English()

        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            self.nlp = None

    def _init_nltk(self):
        """Инициализация NLTK данных"""
        try:
            # Загружаем необходимые данные NLTK
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            logger.info("NLTK data initialized")
        except Exception as e:
            logger.error(f"Error initializing NLTK: {e}")

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Извлечение именованных сущностей (NER)

        Args:
            text: Текст для анализа

        Returns:
            Словарь с категориями сущностей
        """
        if not SPACY_AVAILABLE or not self.nlp:
            logger.warning("spaCy not available. Using fallback entity extraction.")
            return self._fallback_entity_extraction(text)

        try:
            doc = self.nlp(text[:100000])  # Ограничиваем длину для производительности

            entities = {
                'persons': [],
                'organizations': [],
                'locations': [],
                'dates': [],
                'skills': [],
                'other': []
            }

            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'PER']:
                    entities['persons'].append(ent.text)
                elif ent.label_ in ['ORG', 'ORGANIZATION']:
                    entities['organizations'].append(ent.text)
                elif ent.label_ in ['GPE', 'LOC', 'LOCATION']:
                    entities['locations'].append(ent.text)
                elif ent.label_ in ['DATE', 'TIME']:
                    entities['dates'].append(ent.text)
                else:
                    entities['other'].append(ent.text)

            # Удаляем дубликаты
            for key in entities:
                entities[key] = list(set(entities[key]))

            logger.info(f"Extracted {sum(len(v) for v in entities.values())} entities")
            return entities

        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return self._fallback_entity_extraction(text)

    def _fallback_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback метод извлечения сущностей без spaCy"""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'skills': [],
            'other': []
        }

        # Простое извлечение дат
        date_pattern = r'\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        entities['dates'] = list(set(dates))

        return entities

    def extract_keywords_tfidf(
        self,
        texts: List[str],
        top_n: int = 20,
        max_features: int = 100
    ) -> List[Tuple[str, float]]:
        """
        Извлечение ключевых слов с использованием TF-IDF

        Args:
            texts: Список текстов (или один текст в списке)
            top_n: Количество топ ключевых слов
            max_features: Максимальное количество признаков

        Returns:
            Список кортежей (слово, score)
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Using simple keyword extraction.")
            return self._simple_keyword_extraction(texts[0] if texts else "", top_n)

        try:
            # TF-IDF векторизация
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english' if self.language == 'en' else None,
                ngram_range=(1, 2),  # Uni and bigrams
                min_df=1,
                max_df=0.8
            )

            # Если только один текст, добавляем пустой для работы TF-IDF
            if len(texts) == 1:
                texts = texts + [""]

            tfidf_matrix = vectorizer.fit_transform(texts)

            # Получаем feature names и scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix[0].toarray()[0]

            # Создаем список (слово, score)
            word_scores = list(zip(feature_names, scores))

            # Сортируем по score
            word_scores.sort(key=lambda x: x[1], reverse=True)

            logger.info(f"Extracted {len(word_scores[:top_n])} keywords using TF-IDF")
            return word_scores[:top_n]

        except Exception as e:
            logger.error(f"Error in TF-IDF extraction: {e}")
            return self._simple_keyword_extraction(texts[0] if texts else "", top_n)

    def _simple_keyword_extraction(self, text: str, top_n: int) -> List[Tuple[str, float]]:
        """Простое извлечение ключевых слов по частоте"""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

        # Стоп-слова
        stop_words = {
            'have', 'been', 'were', 'with', 'from', 'this', 'that',
            'will', 'would', 'could', 'should', 'more', 'their'
        }

        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)

        return [(word, count) for word, count in word_freq.most_common(top_n)]

    def extract_skills_nlp(self, text: str) -> List[str]:
        """
        Извлечение навыков с использованием NLP

        Args:
            text: Текст резюме

        Returns:
            Список навыков
        """
        skills = set()

        # Расширенный словарь IT навыков
        skill_patterns = {
            # Programming Languages
            'languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
                'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl'
            ],
            # Frameworks
            'frameworks': [
                'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI',
                'Spring', 'Express', 'Laravel', 'Rails', 'ASP.NET', 'Next.js', 'Nuxt'
            ],
            # Databases
            'databases': [
                'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Oracle', 'Cassandra', 'DynamoDB', 'SQLite', 'MariaDB'
            ],
            # DevOps & Cloud
            'devops': [
                'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Jenkins', 'GitLab CI',
                'GitHub Actions', 'Terraform', 'Ansible', 'CI/CD', 'Linux'
            ],
            # ML/AI
            'ml_ai': [
                'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
                'TensorFlow', 'PyTorch', 'scikit-learn', 'Keras', 'Pandas', 'NumPy'
            ],
            # Other
            'other': [
                'Git', 'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
                'JIRA', 'Confluence', 'HTML', 'CSS', 'Sass', 'Webpack'
            ]
        }

        # Поиск по всем категориям
        text_lower = text.lower()
        for category, skill_list in skill_patterns.items():
            for skill in skill_list:
                # Поиск с учетом границ слов
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    skills.add(skill)

        # Если доступен spaCy, используем NER для дополнительных навыков
        if SPACY_AVAILABLE and self.nlp:
            try:
                doc = self.nlp(text[:50000])
                # Ищем существительные и сочетания как потенциальные навыки
                for chunk in doc.noun_chunks:
                    chunk_text = chunk.text.strip()
                    # Фильтруем по длине и наличию технических терминов
                    if 2 <= len(chunk_text.split()) <= 4 and len(chunk_text) < 50:
                        # Простая эвристика: содержит заглавные буквы или цифры
                        if any(c.isupper() or c.isdigit() for c in chunk_text):
                            skills.add(chunk_text)
            except Exception as e:
                logger.debug(f"Error in NER skill extraction: {e}")

        return sorted(list(skills))

    def tokenize(self, text: str) -> List[str]:
        """
        Токенизация текста

        Args:
            text: Текст для токенизации

        Returns:
            Список токенов
        """
        if NLTK_AVAILABLE:
            try:
                from nltk.tokenize import word_tokenize
                tokens = word_tokenize(text)
                logger.debug(f"Tokenized into {len(tokens)} tokens using NLTK")
                return tokens
            except Exception as e:
                logger.debug(f"NLTK tokenization failed: {e}")

        # Fallback: простая токенизация
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    def get_pos_tags(self, text: str) -> List[Tuple[str, str]]:
        """
        Part-of-Speech тэггинг

        Args:
            text: Текст для анализа

        Returns:
            Список кортежей (слово, POS тэг)
        """
        if NLTK_AVAILABLE:
            try:
                from nltk import pos_tag
                tokens = self.tokenize(text)
                tags = pos_tag(tokens)
                logger.debug(f"POS tagged {len(tags)} tokens")
                return tags
            except Exception as e:
                logger.error(f"Error in POS tagging: {e}")

        return []

    def extract_noun_phrases(self, text: str) -> List[str]:
        """
        Извлечение именных групп (noun phrases)

        Args:
            text: Текст для анализа

        Returns:
            Список именных групп
        """
        if not SPACY_AVAILABLE or not self.nlp:
            return []

        try:
            doc = self.nlp(text[:50000])
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            logger.debug(f"Extracted {len(noun_phrases)} noun phrases")
            return noun_phrases
        except Exception as e:
            logger.error(f"Error extracting noun phrases: {e}")
            return []
