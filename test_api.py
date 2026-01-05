"""
Test script for FastAPI endpoints
Tests all API functionality with example requests
"""
import requests
import json
from pathlib import Path
import time

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_health():
    """Test health endpoint"""
    print_section("Test 1: Health Check")

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ API Status: {data['status']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Total Resumes: {data['total_resumes']}")
        print(f"✓ Total Jobs: {data['total_jobs']}")
        print(f"\nComponents:")
        for name, status in data['components'].items():
            print(f"  • {name}: {status}")
        return True
    else:
        print(f"✗ Health check failed: {response.text}")
        return False


def test_list_jobs():
    """Test list jobs endpoint"""
    print_section("Test 2: List Jobs")

    response = requests.get(f"{BASE_URL}/jobs")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total jobs: {data['total']}")

        for i, job in enumerate(data['jobs'][:3], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Required skills: {len(job['required_skills'])}")
        return data['jobs'][0]['job_id'] if data['jobs'] else None
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_upload_resume():
    """Test resume upload endpoint"""
    print_section("Test 3: Upload Resume")

    # Use the real resume file
    resume_path = r"C:\Users\bekmyrza.tursyn\Downloads\Resume2025 (1)-2.pdf"

    if not Path(resume_path).exists():
        print(f"⚠ Resume file not found: {resume_path}")
        print("Skipping upload test")
        return None

    print(f"Uploading: {resume_path}")

    with open(resume_path, 'rb') as f:
        files = {'file': ('resume.pdf', f, 'application/pdf')}
        response = requests.post(
            f"{BASE_URL}/resumes/upload",
            files=files,
            params={'language': 'en'}
        )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['message']}")
        print(f"✓ Resume ID: {data['resume_id']}")
        print(f"✓ Candidate: {data['candidate_name']}")
        print(f"✓ Skills extracted: {len(data['extracted_skills'])}")
        print(f"\nTop skills:")
        for i, skill in enumerate(data['extracted_skills'][:10], 1):
            print(f"  {i}. {skill}")
        return data['resume_id']
    else:
        print(f"✗ Upload failed: {response.text}")
        return None


def test_create_job():
    """Test create job endpoint"""
    print_section("Test 4: Create New Job")

    job_data = {
        "title": "Senior Python ML Engineer",
        "company": "AI Innovations Ltd",
        "description": """
        We're seeking an experienced ML Engineer to build production AI systems.

        Responsibilities:
        - Design and deploy ML models
        - Build data pipelines
        - Work with PyTorch and TensorFlow
        - Optimize model performance

        Requirements:
        - 5+ years Python experience
        - Strong ML and Deep Learning knowledge
        - Experience with PyTorch or TensorFlow
        - AWS/Docker/Kubernetes
        """,
        "required_skills": [
            "Python", "Machine Learning", "Deep Learning",
            "PyTorch", "TensorFlow", "Docker", "AWS"
        ],
        "nice_to_have_skills": [
            "Kubernetes", "MLOps", "Computer Vision", "NLP"
        ],
        "location": "Remote",
        "salary_range": "$120k - $180k"
    }

    response = requests.post(f"{BASE_URL}/jobs", json=job_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Job created!")
        print(f"✓ Job ID: {data['job_id']}")
        print(f"✓ Title: {data['title']}")
        print(f"✓ Company: {data['company']}")
        return data['job_id']
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_recommendations(job_id):
    """Test recommendations endpoint"""
    print_section("Test 5: Get Recommendations")

    if not job_id:
        print("⚠ No job_id provided, skipping test")
        return

    request_data = {
        "job_id": job_id,
        "top_n": 5,
        "matcher_type": "semantic",
        "language": "en"
    }

    print(f"Requesting recommendations for job: {job_id}")
    print(f"Matcher: {request_data['matcher_type']}")
    print(f"Top N: {request_data['top_n']}")

    response = requests.post(f"{BASE_URL}/recommendations", json=request_data)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Recommendations generated!")
        print(f"  Job: {data['job_title']}")
        print(f"  Matcher: {data['matcher_used']}")
        print(f"  Total candidates: {data['total_candidates']}")
        print(f"  Processing time: {data['processing_time_seconds']}s")

        print(f"\n🏆 Top Candidates:")
        for i, candidate in enumerate(data['top_candidates'], 1):
            print(f"\n{i}. {candidate['candidate_name'] or candidate['resume_id']}")
            print(f"   Overall Score: {candidate['overall_score']:.1%}")
            print(f"   Semantic: {candidate['semantic_similarity']:.1%}")
            print(f"   Skills Match: {candidate['skills_match']:.1%}")
            print(f"   Matched Skills ({len(candidate['matched_skills'])}): {', '.join(candidate['matched_skills'][:5])}")
            if candidate['missing_skills']:
                print(f"   Missing Skills: {', '.join(candidate['missing_skills'][:3])}")
    else:
        print(f"✗ Failed: {response.text}")


def test_custom_job_recommendations():
    """Test recommendations with custom job description"""
    print_section("Test 6: Recommendations with Custom Job")

    request_data = {
        "job_description": """
        Looking for a Machine Learning expert with strong Python skills.
        Must have experience with PyTorch, TensorFlow, and deploying models to production.
        Experience with Computer Vision and NLP is a plus.
        """,
        "title": "ML Expert",
        "required_skills": ["Python", "Machine Learning", "PyTorch", "TensorFlow"],
        "top_n": 3,
        "matcher_type": "semantic",
        "language": "ru"  # Test Russian language
    }

    print("Using custom job description (Russian language)")

    response = requests.post(f"{BASE_URL}/recommendations", json=request_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Рекомендации сформированы!")
        print(f"  Вакансия: {data['job_title']}")
        print(f"  Всего кандидатов: {data['total_candidates']}")

        print(f"\n🏆 Топ {len(data['top_candidates'])} кандидатов:")
        for i, candidate in enumerate(data['top_candidates'], 1):
            print(f"\n{i}. {candidate['candidate_name'] or candidate['resume_id']}")
            print(f"   Общий балл: {candidate['overall_score']:.1%}")
    else:
        print(f"✗ Failed: {response.text}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AI Recruiting Agent API - Test Suite")
    print("=" * 60)
    print("\nMake sure the API server is running:")
    print("  python run_api.py")
    print("\nStarting tests in 2 seconds...")
    time.sleep(2)

    try:
        # Test 1: Health check
        if not test_health():
            print("\n✗ API server not responding. Make sure it's running!")
            return

        # Test 2: List jobs
        existing_job_id = test_list_jobs()

        # Test 3: Upload resume
        test_upload_resume()

        # Test 4: Create new job
        new_job_id = test_create_job()

        # Test 5: Get recommendations with existing job
        if existing_job_id:
            test_recommendations(existing_job_id)
        elif new_job_id:
            test_recommendations(new_job_id)

        # Test 6: Custom job recommendations
        test_custom_job_recommendations()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

        print("\n💡 Next steps:")
        print("  • Open http://localhost:8000/docs for interactive API docs")
        print("  • Try different matchers: semantic, tfidf, llm, gemini")
        print("  • Upload more resumes for better matching")

    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to API server!")
        print("Make sure the server is running: python run_api.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
