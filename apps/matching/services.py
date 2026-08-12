import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer, util
from skills_taxonomy.loaders import get_all_skills

# Load spaCy NLP model lazily
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Load SentenceTransformer model lazily
model = None

def get_sentence_transformer():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def extract_skills_from_text(text):
    """Extract skills using spaCy PhraseMatcher + Taxonomy matching."""
    if not text:
        return []

    skills_list = get_all_skills()
    found_skills = set()

    if nlp:
        doc = nlp(text)
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(skill) for skill in skills_list]
        matcher.add("SKILL_MATCHER", patterns)

        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            found_skills.add(span.text)

    # Simple case-insensitive fallback check
    text_lower = text.lower()
    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.add(skill)

    return sorted(list(found_skills))

def calculate_match(resume_text, job_text, resume_skills, job_skills):
    """
    Computes match score combining:
    1. Skill overlap score (60% weight)
    2. Document-level semantic embedding similarity (40% weight)
    """
    resume_skills_set = set(s.lower() for s in resume_skills)
    job_skills_set = set(s.lower() for s in job_skills)

    matched_skills = {}
    missing_skills = {}

    if job_skills_set:
        matched_keys = resume_skills_set.intersection(job_skills_set)
        missing_keys = job_skills_set - resume_skills_set

        # Map back to original casing
        for skill in job_skills:
            if skill.lower() in matched_keys:
                matched_skills[skill] = 0.95
            else:
                missing_skills[skill] = 0.85

        skill_overlap_score = (len(matched_keys) / len(job_skills_set)) * 100
    else:
        skill_overlap_score = 50.0

    # Semantic similarity using sentence-transformers
    try:
        transformer = get_sentence_transformer()
        emb_resume = transformer.encode(resume_text[:2000], convert_to_tensor=True)
        emb_job = transformer.encode(job_text[:2000], convert_to_tensor=True)
        cosine_sim = float(util.cos_sim(emb_resume, emb_job)[0][0])
        semantic_score = max(0.0, min(100.0, cosine_sim * 100))
    except Exception:
        semantic_score = skill_overlap_score

    # Final combined score
    final_score = round((skill_overlap_score * 0.6) + (semantic_score * 0.4), 1)

    # Generate explanation text
    if final_score >= 80:
        explanation = f"Excellent match ({final_score}%). Strong coverage on core skills."
    elif final_score >= 60:
        explanation = f"Good match ({final_score}%). Matched {len(matched_skills)} skills, missing {len(missing_skills)} key skills."
    else:
        explanation = f"Moderate/Low match ({final_score}%). Consider strengthening missing skills: {', '.join(list(missing_skills.keys())[:3])}."

    return {
        'match_score': final_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'explanation': explanation
    }
