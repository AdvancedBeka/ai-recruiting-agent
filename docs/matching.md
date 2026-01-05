# Matching Engine Documentation

## Обзор

Модуль matching обеспечивает сопоставление резюме с вакансиями с использованием трех различных подходов к matching.

## Три подхода к сопоставлению

### 1. Semantic Matcher (Sentence-BERT)

**Принцип работы:**
- Использует sentence-transformers для создания embeddings
- Вычисляет cosine similarity между резюме и описанием вакансии
- Комбинирует семантическое сходство с точным совпадением навыков

**Модель:** `all-MiniLM-L6-v2` (384 dimensions, быстрая)

**Формула итогового score:**
```
overall_score = (semantic_similarity * 0.6) + (skills_match * 0.4)
```

**Преимущества:**
- ✅ Понимает контекст и смысл текста
- ✅ Не требует точного совпадения слов
- ✅ Работает офлайн после загрузки модели
- ✅ Быстрая обработка (batch encoding)

**Недостатки:**
- ❌ Требует ~200MB для модели
- ❌ Медленнее чем TF-IDF
- ❌ Не объясняет почему был дан такой score

### 2. TF-IDF Matcher

**Принцип работы:**
- TF-IDF векторизация текста резюме и вакансии
- Cosine similarity между векторами
- Анализ совпадения навыков

**Формула итогового score:**
```
overall_score = (tfidf_similarity * 0.5) + (skills_match * 0.5)
```

**Преимущества:**
- ✅ Классический проверенный подход
- ✅ Быстрая обработка
- ✅ Легкий вес
- ✅ Легко интерпретировать

**Недостатки:**
- ❌ Не понимает контекст
- ❌ Требует точного совпадения слов
- ❌ Не учитывает семантику

### 3. LLM Matcher (OpenAI GPT)

**Принцип работы:**
- Отправляет резюме и вакансию в GPT-4o (самая мощная модель OpenAI)
- Получает структурированный JSON с score и объяснением
- Комбинирует LLM оценку с точным совпадением навыков

**Формула итогового score:**
```
overall_score = (llm_score * 0.7) + (skills_match * 0.3)
```

**Преимущества:**
- ✅ Наиболее интеллектуальный подход
- ✅ Предоставляет объяснение релевантности
- ✅ Понимает контекст и нюансы
- ✅ Учитывает опыт, образование, проекты

**Недостатки:**
- ❌ Требует API key (платно)
- ❌ Медленнее всех подходов
- ❌ Зависит от внешнего сервиса
- ❌ Результаты могут варьироваться

## Установка

### Базовые зависимости

```bash
pip install pydantic
```

### Для Semantic Matcher

```bash
pip install sentence-transformers
```

При первом запуске модель скачается автоматически (~200MB).

### Для TF-IDF Matcher

```bash
pip install scikit-learn
```

### Для LLM Matcher

```bash
pip install openai
```

И добавьте в `.env`:
```
OPENAI_API_KEY=sk-your-api-key-here
```

## Использование

### Базовое использование

```python
from matching import SemanticMatcher, Job
from resume_parser import TextExtractor

# Parse resume
extractor = TextExtractor()
resume = extractor.parse_resume("resume.pdf")

# Create job
job = Job(
    job_id="job_001",
    title="Python Developer",
    description="Looking for experienced Python developer...",
    required_skills=["Python", "Django", "PostgreSQL"],
    nice_to_have_skills=["Docker", "AWS"]
)

# Match with Semantic Matcher
matcher = SemanticMatcher()
result = matcher.match(resume, job)

print(f"Match score: {result.overall_score:.1%}")
print(f"Matched skills: {', '.join(result.matched_skills)}")
print(f"Missing skills: {', '.join(result.missing_skills)}")
```

### Использование всех трех матчеров

```python
from matching import SemanticMatcher, TFIDFMatcher, LLMMatcher

# Initialize matchers
semantic = SemanticMatcher()
tfidf = TFIDFMatcher(max_features=500)
llm = LLMMatcher(model="gpt-3.5-turbo")

# Match with each
sem_result = semantic.match(resume, job)
tfidf_result = tfidf.match(resume, job)
llm_result = llm.match(resume, job)

print("Comparison:")
print(f"Semantic: {sem_result.overall_score:.1%}")
print(f"TF-IDF: {tfidf_result.overall_score:.1%}")
print(f"LLM: {llm_result.overall_score:.1%}")
```

### Batch matching (топ N резюме)

```python
from matching import SemanticMatcher

matcher = SemanticMatcher()

# Parse multiple resumes
resumes = [extractor.parse_resume(f) for f in resume_files]

# Get top 5 matches
top_matches = matcher.match_many(resumes, job, top_n=5)

for i, result in enumerate(top_matches, 1):
    print(f"{i}. {result.resume_id}: {result.overall_score:.1%}")
```

### Оптимизированный batch matching

```python
# Использует batch encoding для ускорения
top_matches = matcher.match_many_optimized(resumes, job, top_n=5)
```

### Сравнение матчеров

```python
from matching.matcher_comparison import MatcherComparison

# Initialize comparison utility
comparison = MatcherComparison(
    use_semantic=True,
    use_tfidf=True,
    use_llm=True,
    openai_api_key="sk-..."
)

# Compare single resume
result = comparison.compare_single(resume, job)

# Print detailed comparison
comparison.print_comparison(result)

# Get statistics
print(f"Average score: {result.average_score:.1%}")
print(f"Agreement level: {result.agreement_level}")
```

## Job Model

### Создание вакансии

```python
from matching import Job

job = Job(
    job_id="unique_id",
    title="Job Title",
    company="Company Name",  # optional
    description="Full job description...",
    required_skills=["Skill1", "Skill2", "Skill3"],
    nice_to_have_skills=["Skill4", "Skill5"]  # optional
)
```

Поле `full_text` генерируется автоматически из title + company + description.

### Загрузка вакансий из JSON

```python
import json
from matching import Job

with open("jobs.json") as f:
    jobs_data = json.load(f)

jobs = [Job(**job_data) for job_data in jobs_data]
```

## MatchResult Model

Результат сопоставления содержит:

```python
class MatchResult:
    resume_id: str              # ID резюме (file_name)
    job_id: str                 # ID вакансии
    overall_score: float        # 0-1, итоговый score
    skills_match: float         # 0-1, совпадение навыков
    semantic_similarity: float  # 0-1, семантическое сходство
    matched_skills: List[str]   # Совпавшие навыки
    missing_skills: List[str]   # Недостающие навыки
    matching_method: str        # "semantic", "tfidf", или "llm"
    explanation: str            # Объяснение (только для LLM)
```

## Сравнение производительности

| Matcher | Speed | Memory | Accuracy | Offline | Explanation |
|---------|-------|--------|----------|---------|-------------|
| Semantic | Medium | 200MB | High | ✓ | ✗ |
| TF-IDF | Fast | 5MB | Medium | ✓ | ✗ |
| LLM | Slow | Minimal | Highest | ✗ | ✓ |

### Время обработки

| Операция | Semantic | TF-IDF | LLM |
|----------|----------|--------|-----|
| 1 resume | ~0.5s | ~0.1s | ~2-3s |
| 10 resumes (batch) | ~1.5s | ~0.5s | ~20-30s |
| 100 resumes | ~10s | ~3s | ~5 min |

## Рекомендации по использованию

### Когда использовать Semantic Matcher

- ✅ Для большинства случаев (лучший баланс)
- ✅ Когда важна точность
- ✅ Для batch обработки
- ✅ Когда работаете офлайн

### Когда использовать TF-IDF Matcher

- ✅ Для быстрой обработки больших объемов
- ✅ Когда важна скорость
- ✅ Для предварительной фильтрации
- ✅ Когда нужно минимальное потребление памяти

### Когда использовать LLM Matcher

- ✅ Когда нужны объяснения
- ✅ Для финальной проверки топ кандидатов
- ✅ Когда важна максимальная точность
- ✅ Для сложных вакансий требующих нюансов

### Комбинированный подход (Рекомендуется)

```python
# 1. Быстрая фильтрация с TF-IDF
tfidf = TFIDFMatcher()
candidates = tfidf.match_many(all_resumes, job, top_n=20)

# 2. Более точная оценка с Semantic
semantic = SemanticMatcher()
top_candidates = [r for r in all_resumes if r.file_name in [c.resume_id for c in candidates]]
finalists = semantic.match_many(top_candidates, job, top_n=10)

# 3. Финальная проверка и объяснения с LLM
llm = LLMMatcher()
final_top = [r for r in all_resumes if r.file_name in [f.resume_id for f in finalists[:5]]]
final_results = [llm.match(r, job) for r in final_top]

# Показываем с объяснениями
for result in final_results:
    print(f"{result.resume_id}: {result.overall_score:.1%}")
    print(f"Explanation: {result.explanation}\n")
```

## Graceful Degradation

Все матчеры поддерживают fallback режим:

- **SemanticMatcher** → простое сопоставление ключевых слов
- **TFIDFMatcher** → частотный анализ
- **LLMMatcher** → keyword + skills matching

Если библиотеки не установлены, матчеры все равно работают, выдавая warning.

## Примеры

### Пример 1: Найти лучших кандидатов

```python
from matching import SemanticMatcher, Job
from resume_parser import TextExtractor
from pathlib import Path

extractor = TextExtractor()
matcher = SemanticMatcher()

# Parse all resumes
resumes = []
for file in Path("data/resumes").glob("*.pdf"):
    resume = extractor.parse_resume(str(file))
    if resume:
        resumes.append(resume)

# Create job
job = Job(
    job_id="dev_001",
    title="Senior Python Developer",
    description="...",
    required_skills=["Python", "Django", "PostgreSQL"]
)

# Find top 10
top_10 = matcher.match_many(resumes, job, top_n=10)

print("Top 10 Candidates:")
for i, result in enumerate(top_10, 1):
    print(f"{i}. {result.resume_id}")
    print(f"   Score: {result.overall_score:.1%}")
    print(f"   Matched: {', '.join(result.matched_skills[:5])}")
    print()
```

### Пример 2: A/B тестирование матчеров

```python
from matching.matcher_comparison import MatcherComparison

comparison = MatcherComparison(
    use_semantic=True,
    use_tfidf=True,
    use_llm=False
)

# Test on multiple resumes
comparisons = comparison.compare_many(resumes, job, top_n=10)

# Which matcher performs best?
best_matcher = comparison.get_best_matcher(comparisons)
print("Matcher wins:", best_matcher)

# Correlation analysis
correlations = comparison.calculate_correlation(comparisons)
print("Correlations:", correlations)
```

### Пример 3: Объяснение с LLM

```python
from matching import LLMMatcher

llm = LLMMatcher(model="gpt-4o")

result = llm.match(resume, job)

print(f"Score: {result.overall_score:.1%}")
print(f"\nExplanation:")
print(result.explanation)

# Пример вывода:
# Score: 85%
#
# Explanation:
# This candidate is an excellent match for the position. They have 7 years
# of Python experience with strong Django and PostgreSQL skills. The candidate
# has demonstrated experience building scalable systems and leading teams.
# Minor gaps include Kubernetes experience, though they have Docker expertise.
```

## Troubleshooting

### Sentence-transformers не найден

```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Решение:**
```bash
pip install sentence-transformers
```

### Модель не скачивается

```
OSError: Can't load model 'all-MiniLM-L6-v2'
```

**Решение:**
```python
# Скачать вручную
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### OpenAI API ошибка

```
openai.error.AuthenticationError: Incorrect API key
```

**Решение:**
- Проверьте API key в `.env`
- Убедитесь что ключ начинается с `sk-`
- Проверьте баланс на OpenAI

### Медленная работа

**Проблема:** Matching занимает много времени

**Решение:**
- Используйте `match_many_optimized()` для batch
- Используйте TF-IDF для предварительной фильтрации
- Ограничьте длину текста резюме

## API Reference

### SemanticMatcher

```python
class SemanticMatcher(BaseMatcher):
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2')
    def match(self, resume: Resume, job: Job) -> MatchResult
    def match_many(self, resumes: List[Resume], job: Job, top_n: int = 5) -> List[MatchResult]
    def match_many_optimized(self, resumes: List[Resume], job: Job, top_n: int = 5) -> List[MatchResult]
```

### TFIDFMatcher

```python
class TFIDFMatcher(BaseMatcher):
    def __init__(self, max_features: int = 500)
    def match(self, resume: Resume, job: Job) -> MatchResult
```

### LLMMatcher

```python
class LLMMatcher(BaseMatcher):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o")
    def match(self, resume: Resume, job: Job) -> MatchResult
```

### MatcherComparison

```python
class MatcherComparison:
    def __init__(self, use_semantic: bool = True, use_tfidf: bool = True,
                 use_llm: bool = False, openai_api_key: Optional[str] = None)
    def compare_single(self, resume: Resume, job: Job) -> ComparisonResult
    def compare_many(self, resumes: List[Resume], job: Job, top_n: int = 5) -> List[ComparisonResult]
    def print_comparison(self, comparison: ComparisonResult)
    def get_best_matcher(self, comparisons: List[ComparisonResult]) -> Dict[str, int]
    def calculate_correlation(self, comparisons: List[ComparisonResult]) -> Dict[str, float]
```

---

**Версия:** 1.0
**Последнее обновление:** 30.12.2024
**Статус:** Phase 4 Complete ✅
