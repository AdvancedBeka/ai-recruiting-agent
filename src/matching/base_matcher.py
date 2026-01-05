"""
Base Matcher - базовый класс для всех matching подходов
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from .job_model import Job, MatchResult
import sys
from pathlib import Path

# Add resume_parser to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_parser.models import Resume


class BaseMatcher(ABC):
    """
    Базовый класс для всех матчеров

    Определяет общий интерфейс для различных подходов к matching
    """

    def __init__(self):
        """Инициализация матчера"""
        self.name = "Base Matcher"

    @abstractmethod
    def match(self, resume: Resume, job: Job) -> MatchResult:
        """
        Сопоставление одного резюме с одной вакансией

        Args:
            resume: Объект Resume
            job: Объект Job

        Returns:
            MatchResult с оценкой соответствия
        """
        pass

    def match_many(
        self,
        resumes: List[Resume],
        job: Job,
        top_n: int = 5
    ) -> List[MatchResult]:
        """
        Сопоставление множества резюме с одной вакансией

        Args:
            resumes: Список резюме
            job: Вакансия
            top_n: Количество лучших кандидатов

        Returns:
            Список MatchResult, отсортированный по overall_score
        """
        results = []

        for resume in resumes:
            try:
                result = self.match(resume, job)
                results.append(result)
            except Exception as e:
                print(f"Error matching {resume.file_name}: {e}")
                continue

        # Сортируем по overall_score
        results.sort(key=lambda x: x.overall_score, reverse=True)

        return results[:top_n]

    def calculate_skills_match(
        self,
        resume_skills: List[str],
        required_skills: List[str]
    ) -> tuple[float, List[str], List[str]]:
        """
        Вычисление соответствия навыков

        Args:
            resume_skills: Навыки из резюме
            required_skills: Требуемые навыки

        Returns:
            (score, matched_skills, missing_skills)
        """
        if not required_skills:
            return 1.0, [], []

        # Приводим к нижнему регистру для сравнения
        resume_skills_lower = {s.lower() for s in resume_skills}
        required_skills_lower = {s.lower() for s in required_skills}

        # Находим пересечение
        matched = resume_skills_lower.intersection(required_skills_lower)
        missing = required_skills_lower - resume_skills_lower

        # Вычисляем score
        score = len(matched) / len(required_skills_lower) if required_skills_lower else 0.0

        # Возвращаем оригинальные названия навыков
        matched_skills = [s for s in required_skills if s.lower() in matched]
        missing_skills = [s for s in required_skills if s.lower() in missing]

        return score, matched_skills, missing_skills

    def get_stats(self, results: List[MatchResult]) -> Dict:
        """
        Статистика по результатам matching

        Args:
            results: Список MatchResult

        Returns:
            Словарь со статистикой
        """
        if not results:
            return {}

        scores = [r.overall_score for r in results]

        return {
            'total_candidates': len(results),
            'avg_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'method': results[0].matching_method if results else None
        }
