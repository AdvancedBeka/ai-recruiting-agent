"""
Multi-language support (English and Russian)
"""

TRANSLATIONS = {
    "en": {
        "job_not_found": "Job not found",
        "no_job_specified": "Either job_id or job_description must be provided",
        "no_resumes": "No resumes in database",
        "upload_success": "Resume uploaded and parsed successfully",
        "upload_failed": "Failed to parse resume",
        "invalid_file_type": "Invalid file type. Supported: PDF, DOCX, TXT",
        "matcher_not_available": "Matcher type not available",
        "recommendations_generated": "Recommendations generated successfully",
        "top_candidates": "Top candidates",
        "matched_skills": "Matched skills",
        "missing_skills": "Missing skills",
        "overall_score": "Overall score",
        "semantic_similarity": "Semantic similarity",
        "skills_match": "Skills match",
        "explanation": "Explanation",
    },
    "ru": {
        "job_not_found": "Вакансия не найдена",
        "no_job_specified": "Необходимо указать job_id или job_description",
        "no_resumes": "В базе нет резюме",
        "upload_success": "Резюме успешно загружено и обработано",
        "upload_failed": "Не удалось обработать резюме",
        "invalid_file_type": "Неверный тип файла. Поддерживаются: PDF, DOCX, TXT",
        "matcher_not_available": "Указанный тип matcher недоступен",
        "recommendations_generated": "Рекомендации успешно сформированы",
        "top_candidates": "Топ кандидатов",
        "matched_skills": "Совпавшие навыки",
        "missing_skills": "Недостающие навыки",
        "overall_score": "Общий балл",
        "semantic_similarity": "Семантическая схожесть",
        "skills_match": "Совпадение навыков",
        "explanation": "Объяснение",
    },
}


def translate(key: str, language: str = "en") -> str:
    """Get translation for key in specified language"""
    lang = language.lower()
    if lang not in TRANSLATIONS:
        lang = "en"

    return TRANSLATIONS[lang].get(key, key)
