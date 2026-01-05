"""
Sample job descriptions for testing the matching engine
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from matching import Job

# Job 1: Python Backend Developer
python_backend_job = Job(
    job_id="job_001",
    title="Senior Python Backend Developer",
    company="Tech Corp",
    description="""
    We are looking for an experienced Python Backend Developer to join our growing team.

    Responsibilities:
    - Design and develop scalable backend services using Python and Django
    - Build RESTful APIs and microservices
    - Work with PostgreSQL and Redis databases
    - Implement CI/CD pipelines
    - Collaborate with frontend developers and DevOps team

    Requirements:
    - 5+ years of experience with Python
    - Strong knowledge of Django or FastAPI
    - Experience with PostgreSQL, Redis
    - Understanding of Docker and Kubernetes
    - Experience with AWS or similar cloud platforms

    Nice to have:
    - Experience with machine learning
    - Knowledge of GraphQL
    - Contributions to open-source projects
    """,
    required_skills=[
        "Python", "Django", "FastAPI", "PostgreSQL", "Redis",
        "Docker", "Kubernetes", "AWS", "REST API", "Microservices"
    ],
    nice_to_have_skills=[
        "Machine Learning", "GraphQL", "CI/CD", "Jenkins"
    ]
)

# Job 2: Full Stack JavaScript Developer
fullstack_js_job = Job(
    job_id="job_002",
    title="Full Stack JavaScript Developer",
    company="Startup Inc",
    description="""
    Join our startup as a Full Stack JavaScript Developer!

    What you'll do:
    - Build modern web applications with React and Node.js
    - Develop RESTful APIs and real-time features
    - Work with MongoDB and PostgreSQL
    - Implement responsive UI with TypeScript
    - Deploy applications on AWS

    Must have:
    - 3+ years with JavaScript/TypeScript
    - Strong React and Node.js skills
    - Experience with MongoDB or PostgreSQL
    - Knowledge of HTML, CSS, and modern frontend tools

    Bonus:
    - Experience with Next.js
    - Knowledge of Docker
    - Familiar with Agile/Scrum
    """,
    required_skills=[
        "JavaScript", "TypeScript", "React", "Node.js", "Express",
        "MongoDB", "PostgreSQL", "HTML", "CSS", "REST API"
    ],
    nice_to_have_skills=[
        "Next.js", "Docker", "AWS", "Agile", "Scrum"
    ]
)

# Job 3: Machine Learning Engineer
ml_engineer_job = Job(
    job_id="job_003",
    title="Machine Learning Engineer",
    company="AI Solutions",
    description="""
    We're seeking a Machine Learning Engineer to build intelligent systems.

    Key responsibilities:
    - Develop and deploy ML models for production
    - Work with large datasets using Python and SQL
    - Implement NLP and Computer Vision solutions
    - Build data pipelines with Spark
    - Deploy models using Docker and Kubernetes

    Requirements:
    - Strong Python skills (NumPy, Pandas, scikit-learn)
    - Experience with TensorFlow or PyTorch
    - Knowledge of ML algorithms and deep learning
    - SQL and data processing experience
    - Familiar with MLOps practices

    Preferred:
    - PhD or Master's in CS/ML
    - Experience with NLP or Computer Vision
    - Published papers or Kaggle competitions
    """,
    required_skills=[
        "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
        "NumPy", "Pandas", "scikit-learn", "SQL", "Docker", "Kubernetes"
    ],
    nice_to_have_skills=[
        "NLP", "Computer Vision", "Spark", "MLOps", "AWS"
    ]
)

# Job 4: DevOps Engineer
devops_job = Job(
    job_id="job_004",
    title="DevOps Engineer",
    company="Cloud Systems Ltd",
    description="""
    Looking for a DevOps Engineer to manage our cloud infrastructure.

    Responsibilities:
    - Maintain and improve CI/CD pipelines
    - Manage Kubernetes clusters
    - Implement infrastructure as code with Terraform
    - Monitor system performance and reliability
    - Automate deployment processes

    Required:
    - Experience with Docker and Kubernetes
    - Strong knowledge of AWS or Azure
    - Proficient with Linux system administration
    - Experience with CI/CD tools (Jenkins, GitLab CI, GitHub Actions)
    - Knowledge of Terraform or Ansible

    Nice to have:
    - Scripting skills (Python, Bash)
    - Experience with monitoring tools (Prometheus, Grafana)
    - Understanding of security best practices
    """,
    required_skills=[
        "Docker", "Kubernetes", "AWS", "Azure", "Linux",
        "CI/CD", "Jenkins", "Terraform", "Ansible"
    ],
    nice_to_have_skills=[
        "Python", "Bash", "Prometheus", "Grafana", "GitLab CI", "GitHub Actions"
    ]
)

# Job 5: Frontend Developer
frontend_job = Job(
    job_id="job_005",
    title="Frontend Developer (React)",
    company="Design Studio",
    description="""
    We need a talented Frontend Developer to create beautiful UIs.

    What we're looking for:
    - Build responsive web applications with React
    - Implement modern UI/UX designs
    - Write clean, maintainable TypeScript code
    - Work with REST APIs and GraphQL
    - Optimize performance and accessibility

    Must have:
    - 3+ years with React
    - Strong HTML, CSS, and JavaScript skills
    - Experience with TypeScript
    - Knowledge of state management (Redux, Context)
    - Familiar with modern build tools (Webpack, Vite)

    Bonus:
    - Experience with Next.js
    - Knowledge of CSS frameworks (Tailwind, Sass)
    - Testing with Jest and React Testing Library
    """,
    required_skills=[
        "React", "JavaScript", "TypeScript", "HTML", "CSS",
        "Redux", "REST API", "Webpack"
    ],
    nice_to_have_skills=[
        "Next.js", "GraphQL", "Tailwind", "Sass", "Jest", "Vite"
    ]
)

# Export all jobs
SAMPLE_JOBS = [
    python_backend_job,
    fullstack_js_job,
    ml_engineer_job,
    devops_job,
    frontend_job
]

if __name__ == "__main__":
    print("Sample Jobs for Testing")
    print("=" * 60)
    for job in SAMPLE_JOBS:
        print(f"\n{job.job_id}: {job.title}")
        print(f"Company: {job.company}")
        print(f"Required skills ({len(job.required_skills)}): {', '.join(job.required_skills[:5])}...")
        print(f"Nice to have ({len(job.nice_to_have_skills)}): {', '.join(job.nice_to_have_skills[:3])}...")
