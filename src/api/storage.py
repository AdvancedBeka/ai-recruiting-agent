"""
Simple in-memory storage for resumes and jobs
In production, replace with a database (PostgreSQL, MongoDB, etc.)
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from resume_parser.models import Resume
from matching import Job


class ResumeStorage:
    """In-memory storage for parsed resumes"""

    def __init__(self):
        self.resumes: Dict[str, Resume] = {}

    def add_resume(self, resume: Resume) -> str:
        """Add resume to storage"""
        resume_id = resume.file_name
        self.resumes[resume_id] = resume
        return resume_id

    def get_resume(self, resume_id: str) -> Optional[Resume]:
        """Get resume by ID"""
        return self.resumes.get(resume_id)

    def get_all_resumes(self) -> List[Resume]:
        """Get all resumes"""
        return list(self.resumes.values())

    def count(self) -> int:
        """Count total resumes"""
        return len(self.resumes)

    def delete_resume(self, resume_id: str) -> bool:
        """Delete resume"""
        if resume_id in self.resumes:
            del self.resumes[resume_id]
            return True
        return False


class JobStorage:
    """In-memory storage for jobs"""

    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self._load_sample_jobs()

    def _load_sample_jobs(self):
        """Load sample jobs from data/jobs/sample_jobs.py"""
        try:
            from data.jobs.sample_jobs import SAMPLE_JOBS

            for job in SAMPLE_JOBS:
                self.add_job(
                    job_id=job.job_id,
                    title=job.title,
                    company=job.company,
                    description=job.description,
                    required_skills=job.required_skills,
                    nice_to_have_skills=job.nice_to_have_skills,
                )
        except ImportError:
            pass  # Sample jobs not available

    def add_job(
        self,
        job_id: str,
        title: str,
        company: str,
        description: str,
        required_skills: List[str],
        nice_to_have_skills: List[str],
        location: Optional[str] = None,
        salary_range: Optional[str] = None,
    ) -> str:
        """Add job to storage"""
        self.jobs[job_id] = {
            "job_id": job_id,
            "title": title,
            "company": company,
            "description": description,
            "required_skills": required_skills,
            "nice_to_have_skills": nice_to_have_skills,
            "location": location,
            "salary_range": salary_range,
            "created_at": datetime.utcnow().isoformat(),
        }
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        return self.jobs.get(job_id)

    def get_job_as_model(self, job_id: str) -> Optional[Job]:
        """Get job as Job model"""
        job_data = self.get_job(job_id)
        if not job_data:
            return None

        return Job(
            job_id=job_data["job_id"],
            title=job_data["title"],
            company=job_data["company"],
            description=job_data["description"],
            required_skills=job_data["required_skills"],
            nice_to_have_skills=job_data["nice_to_have_skills"],
        )

    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs"""
        return list(self.jobs.values())

    def count(self) -> int:
        """Count total jobs"""
        return len(self.jobs)

    def delete_job(self, job_id: str) -> bool:
        """Delete job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False


# Global instances
resume_storage = ResumeStorage()
job_storage = JobStorage()
