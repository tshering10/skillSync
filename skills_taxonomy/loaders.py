import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = BASE_DIR / 'skills_taxonomy' / 'skills.json'


SKILL_ALIASES = {
    # Web & APIs
    "restful apis": "REST API",
    "restful api": "REST API",
    "rest apis": "REST API",
    "rest api": "REST API",
    "rest": "REST API",
    
    # Frontend Frameworks
    "react.js": "React",
    "reactjs": "React",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "angularjs": "Angular",

    # Backend & Frameworks
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "drf": "Django REST Framework",
    "django rest framework": "Django REST Framework",

    # AI & ML
    "natural language processing": "NLP",
    "nlp": "NLP",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "sentencetransformers": "SentenceTransformers",
    "sentence-transformers": "SentenceTransformers",

    # Cloud, DB & DevOps
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "microservices": "Microservices",
    "microservice": "Microservices",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
    "golang": "Go"
}

def get_canonical_skill(skill_name: str) -> str:
    """Resolves any skill variation or raw text to its canonical name."""
    clean = skill_name.strip().lower()
    return SKILL_ALIASES.get(clean, skill_name.strip())

def load_skills_taxonomy():
    """Loads the skill taxonomy from JSON."""
    if not TAXONOMY_PATH.exists():
        return {}
    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_skills():
    """Returns a flat list of all unique skills and alias patterns."""
    taxonomy = load_skills_taxonomy()
    skills = set()
    for category, skill_list in taxonomy.items():
        for skill in skill_list:
            skills.add(skill)
    for alias in SKILL_ALIASES.keys():
        skills.add(alias)
    return sorted(list(skills))
