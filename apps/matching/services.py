import re
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer, util

from skills_taxonomy.loaders import (
    get_all_skills,
    get_canonical_skill,
)

# ============================================================================
# NLP / MODEL LOADING
# ============================================================================

# Load spaCy lazily / safely
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# SentenceTransformer is loaded lazily because it is relatively expensive
model = None


def get_sentence_transformer():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


# ============================================================================
# PROFILE & ENTITY EXTRACTION PATTERNS
# ============================================================================

COMMON_ROLE_PATTERNS = [
    # Language / Domain specific developers (e.g. Backend-focused Python Developer, Senior Backend Engineer, Full Stack Developer)
    r"\b(?:senior|junior|lead|principal|staff|associate|entry[\s\-]?level)?\s*(?:backend|frontend|full[\s\-]?stack|software|web|mobile|ios|android|cloud|devops|data|ml|ai|machine learning|qa|systems|sre|site reliability|python|java|javascript|golang|go|react|node|django|\.net|c\+\+|rust|php)\s*(?:[-–\s]focused\s+)?(?:[\w\s]{0,15})?(?:engineer|developer|architect|specialist|programmer|lead|consultant)\b",
    
    # Specific specialized & management roles
    r"\b(?:data scientist|data analyst|data engineer|product manager|engineering manager|solution architect|scrum master|technical lead|technical writer)\b",
    
    # Internships & Trainees (e.g. backend development internship, software engineer intern)
    r"\b(?:backend|frontend|software|web|full[\s\-]?stack|python|data)?\s*(?:development\s+)?(?:intern(?:ship)?|trainee)\b",
]

DEGREE_PATTERNS = [
    # Full Degree Names with major (e.g. Bachelor of Information Technology, Master of Science in CS)
    r"\b(?:Bachelor(?:'s)?|Master(?:'s)?|Doctorate|Doctor of Philosophy)\s+(?:of|in)\s+[A-Za-z\s]{3,35}\b",
    
    # Bachelor abbreviations (e.g. B.IT, B.Tech, B.S., B.Sc., B.E., B.C.A., BBA)
    r"\b(?:B\.?I\.?T\.?|B\.?Sc\.?|B\.?S\.?|B\.?Tech|B\.?E\.?|B\.?C\.?A\.?|B\.?B\.?A\.?)\b(?:\s+(?:in|of)\s+[A-Za-z\s]{3,30})?",
    
    # Master abbreviations (e.g. M.Sc., M.S., M.Tech, M.E., M.C.A., MBA)
    r"\b(?:M\.?Sc\.?|M\.?S\.?|M\.?Tech|M\.?E\.?|M\.?C\.?A\.?|M\.?B\.?A\.?)\b(?:\s+(?:in|of)\s+[A-Za-z\s]{3,30})?",
    
    # PhD & Doctorate
    r"\b(?:Ph\.?D\.?)\b(?:\s+(?:in|of)\s+[A-Za-z\s]{3,30})?",
    
    # General degree mentions (e.g. Bachelor's Degree in Computer Science)
    r"\b(?:Bachelor(?:'s)?\s+Degree|Master(?:'s)?\s+Degree)\b(?:\s+(?:in|of)\s+[A-Za-z\s]{3,30})?",
    
    # Secondary education (e.g. +2 Computer Science, +2 Science)
    r"\b\+2\s+(?:in\s+)?[A-Za-z\s]{3,25}\b",
]

# Short skills that require strict case-matching to prevent matching English words
AMBIGUOUS_SHORT_SKILLS = {"Go", "C", "R"}


# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def extract_experience_years(text: str) -> float:
    """
    Extract the highest explicit number of years of experience.
    Examples:
        "5+ years of experience" -> 5.0
        "3 years experience" -> 3.0
    """
    if not text:
        return 0.0

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:professional\s*)?(?:experience|exp)",
        r"(?:experience|exp)\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]

    detected_years = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                detected_years.append(float(match))
            except (ValueError, TypeError):
                continue

    return max(detected_years) if detected_years else 0.0


def extract_roles(text: str) -> list:
    """Extract likely job roles / titles from text."""
    if not text:
        return []

    roles = set()
    for pattern in COMMON_ROLE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = match.group(0).strip()
            cleaned = " ".join(cleaned.split()).title()
            if len(cleaned) > 3:
                roles.add(cleaned)

    return sorted(list(roles))


def extract_education(text: str) -> list:
    """Extract education levels / degrees from text."""
    if not text:
        return []

    education = set()
    for pattern in DEGREE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            raw = match.group(0).strip()
            cleaned = " ".join(raw.split()).title()
            if len(cleaned) > 2:
                education.add(cleaned)

    return sorted(list(education))


def extract_skills_from_text(text: str) -> list:
    """
    Extract technical skills with:
    1. Longest-match-first priority to eliminate false substrings (e.g. Java in JavaScript).
    2. Case-sensitive protection for short words (e.g. 'Go', 'C', 'R').
    3. Non-overlapping token span tracking.
    4. Canonical alias normalization.
    """
    if not text:
        return []

    skills_list = get_all_skills()
    sorted_skills = sorted(skills_list, key=lambda s: len(s), reverse=True)
    
    matched_canonical = set()
    matched_spans = []

    for skill in sorted_skills:
        is_short = skill in AMBIGUOUS_SHORT_SKILLS
        flags = 0 if is_short else re.IGNORECASE
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
        
        for match in re.finditer(pattern, text, flags):
            start, end = match.span()
            
            # Check if this match is already covered by a longer match
            is_overlapping = any(
                m_start <= start and end <= m_end
                for m_start, m_end, _ in matched_spans
            )
            
            if not is_overlapping:
                canonical = get_canonical_skill(skill)
                matched_canonical.add(canonical)
                matched_spans.append((start, end, canonical))

    return sorted(list(matched_canonical))


# ============================================================================
# PROFILE BUILDERS
# ============================================================================

def extract_candidate_profile(text: str) -> dict:
    """
    Build a structured candidate profile from resume text.
    Stored in Resume.candidate_profile.
    """
    return {
        "skills": extract_skills_from_text(text),
        "experience_years": extract_experience_years(text),
        "roles": extract_roles(text),
        "education": extract_education(text),
    }


def extract_job_profile(text: str, title: str = "") -> dict:
    """
    Build a structured job profile from job description text and title.
    Stored in JobDescription.job_profile.
    """
    if title and title.strip():
        roles = [title.strip().title()]
    else:
        roles = extract_roles(text)

    return {
        "skills": extract_skills_from_text(text),
        "required_experience_years": extract_experience_years(text),
        "roles": roles,
        "education": extract_education(text),
    }


# ============================================================================
# DOCUMENT SEMANTIC ENCODING
# ============================================================================

def encode_document(text: str, transformer, chunk_size: int = 1500, overlap: int = 250):
    """
    Encode the complete document without truncating it.
    Long documents are split into overlapping chunks and mean-pooled.
    """
    if not text:
        return transformer.encode("", convert_to_tensor=True)

    text = text.strip()
    if len(text) <= chunk_size:
        return transformer.encode(text, convert_to_tensor=True)

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += chunk_size - overlap

    chunk_embeddings = transformer.encode(chunks, convert_to_tensor=True)
    mean_embedding = chunk_embeddings.mean(dim=0, keepdim=True)
    normalized_embedding = mean_embedding / mean_embedding.norm(dim=1, keepdim=True)
    return normalized_embedding.squeeze(0)


# ============================================================================
# COMPONENT SCORING FUNCTIONS
# ============================================================================

def calculate_role_score(candidate_roles: list, job_roles: list, candidate_text: str = "", job_text: str = "", transformer=None) -> float:
    """Calculate compatibility between candidate roles and job roles."""
    candidate_roles = candidate_roles or []
    job_roles = job_roles or []

    if not candidate_roles and not job_roles:
        return 75.0

    if not candidate_roles:
        return 50.0

    if not job_roles:
        return 75.0

    candidate_lower = {role.lower() for role in candidate_roles}
    job_lower = {role.lower() for role in job_roles}

    # Exact match check
    if candidate_lower.intersection(job_lower):
        return 95.0

    # Semantic comparison
    try:
        if transformer is None:
            transformer = get_sentence_transformer()

        cand_str = " ".join(candidate_roles)
        job_str = " ".join(job_roles)

        cand_emb = transformer.encode(cand_str, convert_to_tensor=True)
        job_emb = transformer.encode(job_str, convert_to_tensor=True)

        cos_sim = float(util.cos_sim(cand_emb, job_emb)[0][0])
        return round(max(0.0, min(100.0, cos_sim * 100)), 1)
    except Exception:
        return 70.0


def calculate_experience_score(candidate_years: float, required_years: float) -> float:
    """Calculate candidate experience fit comparing candidate years vs required years."""
    candidate_years = float(candidate_years or 0.0)
    required_years = float(required_years or 0.0)

    if required_years <= 0:
        return 90.0

    if candidate_years >= required_years:
        return 100.0

    if candidate_years <= 0:
        return 50.0

    ratio = candidate_years / required_years
    return round(max(30.0, min(95.0, ratio * 100)), 1)


def calculate_skill_match(candidate_skills: list, job_skills: list, transformer=None) -> dict:
    """
    Compare candidate skills against required job skills.
    Exact matches receive full credit (1.0).
    Related skills receive soft semantic partial credit (>= 0.70 cosine similarity).
    """
    candidate_skills = candidate_skills or []
    job_skills = job_skills or []

    candidate_canonical = {get_canonical_skill(s) for s in candidate_skills}
    job_canonical = {get_canonical_skill(s) for s in job_skills}

    candidate_by_lower = {s.lower(): s for s in candidate_canonical}
    job_by_lower = {s.lower(): s for s in job_canonical}

    matched_skills = {}
    missing_skills = {}
    matched_points = 0.0

    if not job_by_lower:
        return {
            "score": 65.0,
            "matched_skills": {},
            "missing_skills": {},
        }

    matched_keys = set(candidate_by_lower.keys()) & set(job_by_lower.keys())
    missing_keys = set(job_by_lower.keys()) - set(candidate_by_lower.keys())

    # Exact matches
    for key in matched_keys:
        canonical_name = job_by_lower[key]
        matched_skills[canonical_name] = 1.0
        matched_points += 1.0

    # Semantic partial matches for missing skills
    if missing_keys and candidate_canonical:
        try:
            if transformer is None:
                transformer = get_sentence_transformer()

            cand_list = list(candidate_canonical)
            cand_embeddings = transformer.encode(cand_list, convert_to_tensor=True)

            for key in missing_keys:
                req_skill = job_by_lower[key]
                req_emb = transformer.encode(req_skill, convert_to_tensor=True)
                cos_scores = util.cos_sim(req_emb, cand_embeddings)[0]
                best_idx = int(cos_scores.argmax())
                best_score = float(cos_scores[best_idx])
                best_cand_skill = cand_list[best_idx]

                if best_score >= 0.70:
                    partial_credit = round(min(0.85, best_score * 0.85), 2)
                    matched_skills[f"{req_skill} (~{best_cand_skill})"] = round(best_score, 2)
                    matched_points += partial_credit
                else:
                    missing_skills[req_skill] = 0.85
        except Exception:
            for key in missing_keys:
                missing_skills[job_by_lower[key]] = 0.85
    else:
        for key in missing_keys:
            missing_skills[job_by_lower[key]] = 0.85

    skill_score = round(min(100.0, (matched_points / len(job_by_lower)) * 100), 1)

    return {
        "score": skill_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


# ============================================================================
# RECOMMENDATIONS
# ============================================================================

def generate_recommendations(missing_skills: dict, candidate_years: float, required_years: float, role_score: float) -> list:
    """Generate actionable, constructive recommendations for the candidate."""
    recommendations = []

    # Missing skill suggestions
    if missing_skills:
        top_missing = list(missing_skills.keys())[:3]
        recommendations.append(f"Consider strengthening your experience with: {', '.join(top_missing)}.")

    # Experience gap recommendations
    if required_years > 0 and candidate_years < required_years:
        gap = round(required_years - candidate_years, 1)
        if candidate_years == 0:
            recommendations.append(
                f"This position requests approximately {required_years:.0f}+ years of professional experience. "
                "As an early-career candidate or student, emphasize hands-on projects, system architecture, and practical internships."
            )
        else:
            recommendations.append(
                f"The role requests approximately {required_years:.0f} years of experience, "
                f"while {candidate_years:.1f} years were detected in the resume. Highlighting complex projects "
                f"or leadership experience will help bridge the {gap:.1f}-year gap."
            )

    # Role alignment recommendation
    if role_score < 60.0:
        recommendations.append("Consider tailoring your resume headline and summary to better align with the target role.")

    if not recommendations:
        recommendations.append("Strong alignment! Your profile covers the core requirements of this position.")

    return recommendations


# ============================================================================
# MAIN MATCHING ENGINE
# ============================================================================

def calculate_match(candidate_profile: dict, job_profile: dict, candidate_text: str = "", job_text: str = "") -> dict:
    """
    Calculate the overall SkillSync match score across 4 pillars:
    1. Role Score (20% weight)
    2. Skill Score (45% weight)
    3. Experience Score (15% weight)
    4. Semantic Score (20% weight)
    """
    candidate_profile = candidate_profile or {}
    job_profile = job_profile or {}

    candidate_skills = candidate_profile.get("skills", [])
    candidate_roles = candidate_profile.get("roles", [])
    candidate_years = candidate_profile.get("experience_years", 0.0)

    job_skills = job_profile.get("skills", [])
    job_roles = job_profile.get("roles", [])
    required_years = job_profile.get("required_experience_years", 0.0)

    transformer = get_sentence_transformer()

    # 1. 🎯 ROLE SCORE — 20%
    role_score = calculate_role_score(
        candidate_roles=candidate_roles,
        job_roles=job_roles,
        candidate_text=candidate_text,
        job_text=job_text,
        transformer=transformer,
    )

    # 2. ⏳ EXPERIENCE SCORE — 15%
    experience_score = calculate_experience_score(
        candidate_years=candidate_years,
        required_years=required_years,
    )

    # 3. 🛠️ SKILL SCORE — 45%
    skill_result = calculate_skill_match(
        candidate_skills=candidate_skills,
        job_skills=job_skills,
        transformer=transformer,
    )
    skill_score = skill_result["score"]
    matched_skills = skill_result["matched_skills"]
    missing_skills = skill_result["missing_skills"]

    # 4. 📄 SEMANTIC SCORE — 20%
    try:
        if candidate_text and job_text:
            cand_emb = encode_document(candidate_text, transformer)
            job_emb = encode_document(job_text, transformer)
            cos_sim = float(util.cos_sim(cand_emb, job_emb)[0][0])
            semantic_score = round(max(0.0, min(100.0, cos_sim * 100)), 1)
        else:
            semantic_score = 50.0
    except Exception:
        semantic_score = 50.0

    # 5. OVERALL WEIGHTED SCORE
    weighted_score = (
        (role_score * 0.20)
        + (skill_score * 0.45)
        + (experience_score * 0.15)
        + (semantic_score * 0.20)
    )
    final_score = round(max(0.0, min(100.0, weighted_score)), 1)

    # 6. RECOMMENDATIONS & EXPLANATION
    recommendations = generate_recommendations(
        missing_skills=missing_skills,
        candidate_years=candidate_years,
        required_years=required_years,
        role_score=role_score,
    )

    if final_score >= 80:
        explanation = f"Excellent match ({final_score}%). Strong alignment across role, skills, and experience."
    elif final_score >= 60:
        explanation = f"Good match ({final_score}%). Skill fit is {skill_score}%, experience fit is {experience_score}%, and role fit is {role_score}%."
    else:
        top_missing = ", ".join(list(missing_skills.keys())[:3]) if missing_skills else "core requirements"
        explanation = f"Moderate/low match ({final_score}%). Key areas for improvement include: {top_missing}."

    return {
        "match_score": final_score,
        "role_score": role_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "semantic_score": semantic_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
        "explanation": explanation,
    }