import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = BASE_DIR / "skills_taxonomy" / "skills.json"

# SKILL ALIASES


SKILL_ALIASES = {

    "python": "Python",

    "javascript": "JavaScript",
    "js": "JavaScript",

    "typescript": "TypeScript",
    "ts": "TypeScript",

    "golang": "Go",

    "c sharp": "C#",
    "c#": "C#",

    "c plus plus": "C++",
    "c++": "C++",

    # Backend / Frameworks

    "django": "Django",

    "django rest framework": "Django REST Framework",
    "django-rest-framework": "Django REST Framework",
    "drf": "Django REST Framework",

    "fast api": "FastAPI",

    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",

    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",

    "nextjs": "Next.js",
    "next.js": "Next.js",

    "reactjs": "React",
    "react.js": "React",

    "vuejs": "Vue.js",
    "vue.js": "Vue.js",

    "angularjs": "Angular",

    # APIs


    "rest": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    "websocket": "WebSockets",
    "websockets": "WebSockets",

    # Databases


    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",

    "mysql": "MySQL",

    "mongo": "MongoDB",
    "mongodb": "MongoDB",

    "redis": "Redis",


    # Cloud

    "aws": "AWS",
    "amazon web services": "AWS",

    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",

    "azure": "Azure",
    "microsoft azure": "Azure",

    # DevOps

    "docker": "Docker",
    "docker compose": "Docker Compose",

    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",

    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous delivery": "CI/CD",

    "github actions": "GitHub Actions",

    "gitlab ci": "GitLab CI",

    # Machine Learning / AI

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "deep learning": "Deep Learning",
    "dl": "Deep Learning",

    "natural language processing": "NLP",
    "nlp": "NLP",

    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",

    "sentence transformers": "SentenceTransformers",
    "sentence-transformers": "SentenceTransformers",
    "sentencetransformers": "SentenceTransformers",

    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",

    # Data Science / Analytics

    "pandas": "Pandas",
    "numpy": "NumPy",

    "matplotlib": "Matplotlib",

    "seaborn": "Seaborn",

    "jupyter": "Jupyter Notebook",
    "jupyter notebook": "Jupyter Notebook",

    "powerbi": "Power BI",
    "power bi": "Power BI",
    "microsoft power bi": "Power BI",

    "tableau": "Tableau",

    "excel": "Excel",
    "microsoft excel": "Excel",

    "statistical analysis": "Statistical Analysis",
    "statistical analytics": "Statistical Analysis",

    "statistics": "Statistics",

    "data analysis": "Data Analysis",

    "data visualization": "Data Visualization",

    "data cleaning": "Data Cleaning",

    "exploratory data analysis": "Exploratory Data Analysis",
    "eda": "Exploratory Data Analysis",

    "feature engineering": "Feature Engineering",
    # Architecture

    "microservice": "Microservices",
    "microservices": "Microservices",

    "distributed system": "Distributed Systems",
    "distributed systems": "Distributed Systems",

    "message queue": "Message Queues",
    "message queues": "Message Queues",

    "event driven architecture": "Event-Driven Architecture",
    "event-driven architecture": "Event-Driven Architecture",

    # Tools

    "git": "Git",

    "github": "GitHub",

    "gitlab": "GitLab",

    "postman": "Postman",

    "pytest": "pytest",
}

# CANONICAL SKILL LOOKUP

def get_canonical_skill(skill_name: str) -> str:
    """
    Convert a skill name or alias into its canonical form.

    Examples:
        Google Cloud -> GCP
        google cloud -> GCP
        sklearn -> scikit-learn
        DRF -> Django REST Framework
        RESTful APIs -> REST API
    """

    if not skill_name:
        return ""

    clean = skill_name.strip().lower()

    # Direct alias lookup
    if clean in SKILL_ALIASES:
        return SKILL_ALIASES[clean]

    # Case-insensitive taxonomy lookup
    taxonomy = load_skills_taxonomy()

    for skill_list in taxonomy.values():
        for canonical_skill in skill_list:
            if canonical_skill.lower() == clean:
                return canonical_skill

    # Unknown skill — preserve original formatting
    return skill_name.strip()

# TAXONOMY LOADING

def load_skills_taxonomy():
    """
    Load skills taxonomy from skills.json.
    """

    if not TAXONOMY_PATH.exists():
        return {}

    try:
        with open(TAXONOMY_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def get_all_skills():
    """
    Return a flat list containing:

    1. Canonical taxonomy skills
    2. Alias patterns used by the extractor
    """

    taxonomy = load_skills_taxonomy()

    skills = set()

    # Canonical taxonomy skills
    for skill_list in taxonomy.values():
        for skill in skill_list:
            skills.add(skill)

    # Alias forms
    for alias in SKILL_ALIASES.keys():
        skills.add(alias)

    return sorted(skills, key=len, reverse=True)