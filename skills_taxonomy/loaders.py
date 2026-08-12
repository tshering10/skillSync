import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = BASE_DIR / 'skills_taxonomy' / 'skills.json'

def load_skills_taxonomy():
    """Loads the skill taxonomy from JSON."""
    if not TAXONOMY_PATH.exists():
        return {}
    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_skills():
    """Returns a flat list of all unique skills in lowercase and original form."""
    taxonomy = load_skills_taxonomy()
    skills = set()
    for category, skill_list in taxonomy.items():
        for skill in skill_list:
            skills.add(skill)
    return sorted(list(skills))
