"""
Matcher Comparison Utility

Позволяет сравнить результаты всех трех подходов к matching
"""
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import statistics

from .job_model import Job, MatchResult
from .semantic_matcher import SemanticMatcher
from .tfidf_matcher import TFIDFMatcher
from .llm_matcher import LLMMatcher

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_parser.models import Resume

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """Результат сравнения матчеров"""
    resume_id: str
    job_id: str

    # Результаты от каждого матчера
    semantic_result: Optional[MatchResult] = None
    tfidf_result: Optional[MatchResult] = None
    llm_result: Optional[MatchResult] = None

    # Сводная статистика
    average_score: float = 0.0
    median_score: float = 0.0
    score_variance: float = 0.0
    agreement_level: str = "unknown"  # high, medium, low

    def __post_init__(self):
        """Вычисляем статистику после инициализации"""
        scores = []

        if self.semantic_result:
            scores.append(self.semantic_result.overall_score)
        if self.tfidf_result:
            scores.append(self.tfidf_result.overall_score)
        if self.llm_result:
            scores.append(self.llm_result.overall_score)

        if len(scores) >= 2:
            self.average_score = statistics.mean(scores)
            self.median_score = statistics.median(scores)
            self.score_variance = statistics.variance(scores) if len(scores) > 1 else 0.0

            # Определяем уровень согласованности
            if self.score_variance < 0.01:
                self.agreement_level = "high"
            elif self.score_variance < 0.05:
                self.agreement_level = "medium"
            else:
                self.agreement_level = "low"


class MatcherComparison:
    """
    Утилита для сравнения различных подходов к matching

    Использует все три матчера и предоставляет сравнительный анализ
    """

    def __init__(
        self,
        use_semantic: bool = True,
        use_tfidf: bool = True,
        use_llm: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Args:
            use_semantic: Использовать Semantic Matcher
            use_tfidf: Использовать TF-IDF Matcher
            use_llm: Использовать LLM Matcher
            openai_api_key: API ключ для OpenAI (если use_llm=True)
        """
        self.matchers = {}

        if use_semantic:
            try:
                self.matchers['semantic'] = SemanticMatcher()
                logger.info("Semantic Matcher initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Semantic Matcher: {e}")

        if use_tfidf:
            try:
                self.matchers['tfidf'] = TFIDFMatcher()
                logger.info("TF-IDF Matcher initialized")
            except Exception as e:
                logger.warning(f"Could not initialize TF-IDF Matcher: {e}")

        if use_llm:
            try:
                self.matchers['llm'] = LLMMatcher(api_key=openai_api_key)
                logger.info("LLM Matcher initialized")
            except Exception as e:
                logger.warning(f"Could not initialize LLM Matcher: {e}")

        if not self.matchers:
            logger.error("No matchers available!")

    def compare_single(self, resume: Resume, job: Job) -> ComparisonResult:
        """
        Сравнить одно резюме с одной вакансией используя все доступные матчеры

        Args:
            resume: Резюме
            job: Вакансия

        Returns:
            ComparisonResult с результатами от всех матчеров
        """
        result = ComparisonResult(
            resume_id=resume.file_name,
            job_id=job.job_id
        )

        # Запускаем каждый матчер
        if 'semantic' in self.matchers:
            try:
                result.semantic_result = self.matchers['semantic'].match(resume, job)
                logger.info(f"Semantic match: {result.semantic_result.overall_score:.1%}")
            except Exception as e:
                logger.error(f"Semantic matching failed: {e}")

        if 'tfidf' in self.matchers:
            try:
                result.tfidf_result = self.matchers['tfidf'].match(resume, job)
                logger.info(f"TF-IDF match: {result.tfidf_result.overall_score:.1%}")
            except Exception as e:
                logger.error(f"TF-IDF matching failed: {e}")

        if 'llm' in self.matchers:
            try:
                result.llm_result = self.matchers['llm'].match(resume, job)
                logger.info(f"LLM match: {result.llm_result.overall_score:.1%}")
            except Exception as e:
                logger.error(f"LLM matching failed: {e}")

        # Статистика вычисляется в __post_init__
        return result

    def compare_many(
        self,
        resumes: List[Resume],
        job: Job,
        top_n: int = 5
    ) -> List[ComparisonResult]:
        """
        Сравнить несколько резюме с вакансией

        Args:
            resumes: Список резюме
            job: Вакансия
            top_n: Сколько топ результатов вернуть

        Returns:
            Список ComparisonResult, отсортированный по average_score
        """
        results = []

        for resume in resumes:
            comparison = self.compare_single(resume, job)
            results.append(comparison)

        # Сортируем по среднему score
        results.sort(key=lambda x: x.average_score, reverse=True)

        return results[:top_n]

    def print_comparison(self, comparison: ComparisonResult):
        """
        Красиво выводит результат сравнения

        Args:
            comparison: Результат сравнения
        """
        print("\n" + "=" * 70)
        print(f"Comparison Results: {comparison.resume_id} vs {comparison.job_id}")
        print("=" * 70)

        print(f"\n{'Matcher':<20} {'Score':<10} {'Semantic/LLM':<15} {'Skills':<10}")
        print("-" * 70)

        if comparison.semantic_result:
            r = comparison.semantic_result
            print(f"{'Sentence-BERT':<20} {r.overall_score:<10.1%} "
                  f"{r.semantic_similarity:<15.1%} {r.skills_match:<10.1%}")

        if comparison.tfidf_result:
            r = comparison.tfidf_result
            sem = r.semantic_similarity if r.semantic_similarity else 0.0
            print(f"{'TF-IDF':<20} {r.overall_score:<10.1%} "
                  f"{sem:<15.1%} {r.skills_match:<10.1%}")

        if comparison.llm_result:
            r = comparison.llm_result
            sem = r.semantic_similarity if r.semantic_similarity else 0.0
            print(f"{'LLM (GPT)':<20} {r.overall_score:<10.1%} "
                  f"{sem:<15.1%} {r.skills_match:<10.1%}")

        print("\n" + "-" * 70)
        print(f"Average Score: {comparison.average_score:.1%}")
        print(f"Median Score: {comparison.median_score:.1%}")
        print(f"Variance: {comparison.score_variance:.4f}")
        print(f"Agreement Level: {comparison.agreement_level.upper()}")

        # Skills analysis
        if comparison.semantic_result:
            r = comparison.semantic_result
            print(f"\n📊 Skills Analysis:")
            print(f"  Matched: {', '.join(r.matched_skills[:8])}")
            if r.missing_skills:
                print(f"  Missing: {', '.join(r.missing_skills[:5])}")

        # LLM explanation
        if comparison.llm_result and comparison.llm_result.explanation:
            print(f"\n💡 LLM Explanation:")
            print(f"  {comparison.llm_result.explanation[:200]}...")

    def get_best_matcher(self, comparisons: List[ComparisonResult]) -> Dict[str, int]:
        """
        Определяет какой матчер чаще всего дает наилучшие результаты

        Args:
            comparisons: Список результатов сравнения

        Returns:
            Словарь {matcher_name: count} с количеством побед
        """
        wins = {'semantic': 0, 'tfidf': 0, 'llm': 0}

        for comp in comparisons:
            scores = {}

            if comp.semantic_result:
                scores['semantic'] = comp.semantic_result.overall_score
            if comp.tfidf_result:
                scores['tfidf'] = comp.tfidf_result.overall_score
            if comp.llm_result:
                scores['llm'] = comp.llm_result.overall_score

            if scores:
                winner = max(scores.items(), key=lambda x: x[1])
                wins[winner[0]] += 1

        return wins

    def calculate_correlation(self, comparisons: List[ComparisonResult]) -> Dict[str, float]:
        """
        Вычисляет корреляцию между результатами разных матчеров

        Args:
            comparisons: Список результатов сравнения

        Returns:
            Словарь с корреляциями между парами матчеров
        """
        semantic_scores = []
        tfidf_scores = []
        llm_scores = []

        for comp in comparisons:
            if comp.semantic_result:
                semantic_scores.append(comp.semantic_result.overall_score)
            if comp.tfidf_result:
                tfidf_scores.append(comp.tfidf_result.overall_score)
            if comp.llm_result:
                llm_scores.append(comp.llm_result.overall_score)

        correlations = {}

        # Простая корреляция Пирсона
        if len(semantic_scores) == len(tfidf_scores) and len(semantic_scores) > 1:
            try:
                corr = statistics.correlation(semantic_scores, tfidf_scores)
                correlations['semantic_vs_tfidf'] = corr
            except:
                pass

        if len(semantic_scores) == len(llm_scores) and len(semantic_scores) > 1:
            try:
                corr = statistics.correlation(semantic_scores, llm_scores)
                correlations['semantic_vs_llm'] = corr
            except:
                pass

        if len(tfidf_scores) == len(llm_scores) and len(tfidf_scores) > 1:
            try:
                corr = statistics.correlation(tfidf_scores, llm_scores)
                correlations['tfidf_vs_llm'] = corr
            except:
                pass

        return correlations
