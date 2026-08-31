from sentence_transformers import util

from .document_parser import get_sentence_transformer, encode_document
from .llm_service import extract_candidate_profile_llm as extract_candidate_profile, extract_job_profile_llm as extract_job_profile


# Component scoring functions
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


def calculate_experience_score(candidate_years: float, required_years: float, candidate_details: dict = None, job_details: dict = None) -> float:
    """
    Calculate candidate experience fit comparing candidate years vs required years
    and supporting experience ranges.
    """
    candidate_years = float(candidate_years or 0.0)
    required_years = float(required_years or 0.0)

    # Check for min_years in job_details
    min_required = required_years
    if job_details and "min_years" in job_details and job_details["min_years"] > 0:
        min_required = float(job_details["min_years"])

    if min_required <= 0:
        return 90.0

    if candidate_years >= min_required:
        return 100.0

    if candidate_years <= 0:
        return 50.0

    ratio = candidate_years / min_required
    return round(max(30.0, min(95.0, ratio * 100)), 1)


def calculate_education_score(candidate_education: list, job_education: list, candidate_details: list = None, job_details: list = None) -> float:
    """
    Calculate education alignment comparing degree hierarchy rank (0-4) and field of study.
    Hierarchy: Doctorate (4) > Master (3) > Bachelor (2) > Associate/Diploma (1) > Other (0).
    """
    candidate_details = candidate_details or []
    job_details = job_details or []

    # If Job Description has no specific education requirement, award neutral high fit
    if not job_details and not job_education:
        return 90.0

    # Determine highest required degree rank
    if job_details:
        highest_req_rank = max(d.get("hierarchy_rank", 2) for d in job_details)
        req_fields = {d.get("field_of_study", "General") for d in job_details}
    else:
        highest_req_rank = 2  # Default to Bachelor
        req_fields = {"General", "Computer Science", "Information Technology", "Software Engineering"}

    # Determine highest candidate degree rank
    if candidate_details:
        highest_cand_rank = max(d.get("hierarchy_rank", 0) for d in candidate_details)
        cand_fields = {d.get("field_of_study", "General") for d in candidate_details}
    elif candidate_education:
        highest_cand_rank = 2
        cand_fields = {"General"}
    else:
        highest_cand_rank = 0
        cand_fields = set()

    # If candidate degree rank meets or exceeds job requirement
    if highest_cand_rank >= highest_req_rank:
        # Check field alignment
        if cand_fields.intersection(req_fields) or "General" in req_fields or "General" in cand_fields:
            return 100.0
        return 90.0

    # If candidate is 1 rank below (e.g. Associate vs Bachelor)
    if highest_cand_rank == highest_req_rank - 1:
        return 75.0

    # If candidate has lower / no degree
    if highest_cand_rank > 0:
        return 60.0

    return 50.0


def calculate_skill_match(
    candidate_skills: list,
    job_skills: list,
    required_skills: list = None,
    preferred_skills: list = None,
    skill_groups: list = None,
    transformer=None
) -> dict:
    """
    Compare candidate skills against job skills with:
    1. Skill Groups / Alternatives ("OR" dependencies: satisfying one satisfies the group).
    2. Required vs. Preferred skill weighting (80% required / 20% preferred).
    3. Exact and soft semantic matching (cosine similarity >= 0.70).
    """
    candidate_skills = candidate_skills or []
    job_skills = job_skills or []
    skill_groups = skill_groups or []

    # Gemini already canonicalizes skill names — use lowercase for comparison
    candidate_canonical = {s.strip() for s in candidate_skills}
    candidate_by_lower = {s.lower(): s for s in candidate_canonical}

    # Determine required and preferred skill lists
    if required_skills is not None or preferred_skills is not None:
        req_set = {s.strip() for s in (required_skills or [])}
        pref_set = {s.strip() for s in (preferred_skills or [])} - req_set
    else:
        req_set = {s.strip() for s in job_skills}
        pref_set = set()

    matched_skills = {}
    missing_skills = {}

    # 1. Process Skill Groups (Alternative "OR" requirements)
    group_consumed_skills = set()
    group_matched_points = 0.0
    group_total_count = len(skill_groups)

    if transformer is None and (candidate_canonical or skill_groups):
        transformer = get_sentence_transformer()

    cand_list = list(candidate_canonical)
    cand_embeddings = None
    if cand_list and transformer is not None:
        try:
            cand_embeddings = transformer.encode(cand_list, convert_to_tensor=True)
        except Exception:
            cand_embeddings = None

    for group in skill_groups:
        g_skills = [s.strip() for s in group.get("skills", [])]
        group_consumed_skills.update(g_skills)

        # Check if candidate has ANY exact match in this alternative group
        exact_matches = [s for s in g_skills if s.lower() in candidate_by_lower]
        if exact_matches:
            matched_skill = exact_matches[0]
            matched_skills[f"{matched_skill} (satisfies {'/'.join(g_skills)})"] = 1.0
            group_matched_points += 1.0
            continue

        # Check semantic similarity to any skill in the group
        best_group_score = 0.0
        best_match_pair = None

        if cand_embeddings is not None and g_skills:
            for g_skill in g_skills:
                try:
                    req_emb = transformer.encode(g_skill, convert_to_tensor=True)
                    cos_scores = util.cos_sim(req_emb, cand_embeddings)[0]
                    b_idx = int(cos_scores.argmax())
                    b_score = float(cos_scores[b_idx])
                    if b_score > best_group_score:
                        best_group_score = b_score
                        best_match_pair = (g_skill, cand_list[b_idx])
                except Exception:
                    pass

        if best_group_score >= 0.70 and best_match_pair:
            req_name, cand_name = best_match_pair
            partial_credit = round(min(0.85, best_group_score * 0.85), 2)
            matched_skills[f"{req_name} (~{cand_name}) [satisfies {'/'.join(g_skills)}]"] = round(best_group_score, 2)
            group_matched_points += partial_credit
        else:
            missing_skills[f"One of: {', '.join(g_skills)}"] = 0.90

    # Remove group skills from individual required/preferred lists so they aren't counted twice
    standalone_req = req_set - group_consumed_skills
    standalone_pref = pref_set - group_consumed_skills

    # 2. Evaluate Standalone Required Skills
    req_matched_points = 0.0
    for req_skill in standalone_req:
        req_lower = req_skill.lower()
        if req_lower in candidate_by_lower:
            matched_skills[req_skill] = 1.0
            req_matched_points += 1.0
        else:
            # Check semantic soft match
            soft_matched = False
            if cand_embeddings is not None:
                try:
                    req_emb = transformer.encode(req_skill, convert_to_tensor=True)
                    cos_scores = util.cos_sim(req_emb, cand_embeddings)[0]
                    best_idx = int(cos_scores.argmax())
                    best_score = float(cos_scores[best_idx])
                    if best_score >= 0.70:
                        partial_credit = round(min(0.85, best_score * 0.85), 2)
                        matched_skills[f"{req_skill} (~{cand_list[best_idx]})"] = round(best_score, 2)
                        req_matched_points += partial_credit
                        soft_matched = True
                except Exception:
                    pass

            if not soft_matched:
                missing_skills[req_skill] = 1.0

    # 3. Evaluate Standalone Preferred Skills
    pref_matched_points = 0.0
    for pref_skill in standalone_pref:
        pref_lower = pref_skill.lower()
        if pref_lower in candidate_by_lower:
            matched_skills[f"{pref_skill} (Preferred)"] = 1.0
            pref_matched_points += 1.0
        else:
            soft_matched = False
            if cand_embeddings is not None:
                try:
                    pref_emb = transformer.encode(pref_skill, convert_to_tensor=True)
                    cos_scores = util.cos_sim(pref_emb, cand_embeddings)[0]
                    best_idx = int(cos_scores.argmax())
                    best_score = float(cos_scores[best_idx])
                    if best_score >= 0.70:
                        partial_credit = round(min(0.85, best_score * 0.85), 2)
                        matched_skills[f"{pref_skill} (Preferred ~{cand_list[best_idx]})"] = round(best_score, 2)
                        pref_matched_points += partial_credit
                        soft_matched = True
                except Exception:
                    pass

            if not soft_matched:
                missing_skills[f"{pref_skill} (Preferred)"] = 0.50

    # 4. Calculate Final Weighted Skill Score
    total_req_units = len(standalone_req) + group_total_count
    total_req_earned = req_matched_points + group_matched_points

    if total_req_units > 0:
        req_score = (total_req_earned / total_req_units) * 100.0
    else:
        req_score = 80.0 if not standalone_pref else 100.0

    total_pref_units = len(standalone_pref)
    if total_pref_units > 0:
        pref_score = (pref_matched_points / total_pref_units) * 100.0
        skill_score = round(min(100.0, (req_score * 0.80) + (pref_score * 0.20)), 1)
    else:
        skill_score = round(min(100.0, req_score), 1)

    if not req_set and not pref_set and not skill_groups:
        skill_score = 65.0

    return {
        "score": skill_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


# Recommendations
def generate_recommendations(missing_skills: dict, candidate_years: float, required_years: float, role_score: float, education_score: float = 100.0) -> list:
    """Generate actionable, constructive recommendations for the candidate."""
    recommendations = []

    # Required vs Preferred missing skill suggestions
    if missing_skills:
        req_missing = [s for s in missing_skills.keys() if "(Preferred)" not in s]
        pref_missing = [s.replace(" (Preferred)", "") for s in missing_skills.keys() if "(Preferred)" in s]

        if req_missing:
            top_req = req_missing[:3]
            recommendations.append(f"Core requirements to focus on: {', '.join(top_req)}.")

        if pref_missing and len(recommendations) < 2:
            top_pref = pref_missing[:2]
            recommendations.append(f"Nice-to-have skills that will strengthen your profile: {', '.join(top_pref)}.")

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

    # Education recommendation
    if education_score < 70.0:
        recommendations.append("Highlight relevant certifications, technical coursework, or practical project experience to complement academic background.")

    if not recommendations:
        recommendations.append("Strong alignment! Your profile covers the core requirements of this position.")

    return recommendations


# Main matching engine
def calculate_match(
    candidate_profile=None,
    job_profile=None,
    candidate_text: str = "",
    job_text: str = "",
    candidate_skills: list = None,
    job_skills: list = None,
    *args,
    **kwargs
) -> dict:
    """
    Calculate the overall SkillSync match score across 5 pillars:
    1. Skill Score (40% weight) - Handles required, preferred & alternative OR groups
    2. Role Score (20% weight) - Role & title alignment
    3. Experience Score (15% weight) - Seniority & experience ranges
    4. Education Score (10% weight) - Degree hierarchy & major relevance
    5. Semantic Score (15% weight) - Full document contextual similarity
    """
    # Handle flexible calling conventions (e.g. passing raw text strings as first arguments)
    if isinstance(candidate_profile, str):
        candidate_text = candidate_profile
        candidate_profile = extract_candidate_profile(candidate_text)
    elif candidate_profile is None:
        candidate_profile = extract_candidate_profile(candidate_text) if candidate_text else {}

    if isinstance(job_profile, str):
        job_text = job_profile
        job_profile = extract_job_profile(job_text)
    elif job_profile is None:
        job_profile = extract_job_profile(job_text) if job_text else {}

    # Override skills if explicitly passed
    if candidate_skills is not None:
        candidate_profile["skills"] = candidate_skills
    if job_skills is not None:
        job_profile["skills"] = job_skills

    cand_skills = candidate_profile.get("skills", [])
    cand_roles = candidate_profile.get("roles", [])
    cand_years = candidate_profile.get("experience_years", 0.0)
    cand_exp_details = candidate_profile.get("experience_details", {})
    cand_edu = candidate_profile.get("education", [])
    cand_edu_details = candidate_profile.get("education_details", [])

    j_skills = job_profile.get("skills", [])
    j_roles = job_profile.get("roles", [])
    req_skills = job_profile.get("required_skills", None)
    pref_skills = job_profile.get("preferred_skills", None)
    skill_groups = job_profile.get("skill_groups", [])
    req_years = job_profile.get("required_experience_years", 0.0)
    j_exp_details = job_profile.get("experience_details", {})
    j_edu = job_profile.get("education", [])
    j_edu_details = job_profile.get("education_details", [])

    transformer = get_sentence_transformer()

    # 1. Role Score — 20%
    role_score = calculate_role_score(
        candidate_roles=cand_roles,
        job_roles=j_roles,
        candidate_text=candidate_text,
        job_text=job_text,
        transformer=transformer,
    )

    # 2. Skill Score — 40%
    skill_result = calculate_skill_match(
        candidate_skills=cand_skills,
        job_skills=j_skills,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        skill_groups=skill_groups,
        transformer=transformer,
    )
    skill_score = skill_result["score"]
    matched_skills = skill_result["matched_skills"]
    missing_skills = skill_result["missing_skills"]

    # 3. Experience Score — 15%
    experience_score = calculate_experience_score(
        candidate_years=cand_years,
        required_years=req_years,
        candidate_details=cand_exp_details,
        job_details=j_exp_details,
    )

    # 4. Education Score — 10%
    education_score = calculate_education_score(
        candidate_education=cand_edu,
        job_education=j_edu,
        candidate_details=cand_edu_details,
        job_details=j_edu_details,
    )

    # 5. Semantic Score — 15%
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

    # 6. Overall weighted score
    weighted_score = (
        (role_score * 0.20)
        + (skill_score * 0.40)
        + (experience_score * 0.15)
        + (education_score * 0.10)
        + (semantic_score * 0.15)
    )
    final_score = round(max(0.0, min(100.0, weighted_score)), 1)

    # 7. Recommendations & explanation
    recommendations = generate_recommendations(
        missing_skills=missing_skills,
        candidate_years=cand_years,
        required_years=req_years,
        role_score=role_score,
        education_score=education_score,
    )

    if final_score >= 80:
        explanation = f"Excellent match ({final_score}%). Strong alignment across role, skills, and experience."
    elif final_score >= 60:
        explanation = f"Good match ({final_score}%). Skill fit is {skill_score}%, experience fit is {experience_score}%, and role fit is {role_score}%."
    else:
        req_missing = [s for s in missing_skills.keys() if "(Preferred)" not in s]
        top_missing = ", ".join(req_missing[:3]) if req_missing else "core requirements"
        explanation = f"Moderate/low match ({final_score}%). Key areas for improvement include: {top_missing}."

    return {
        "match_score": final_score,
        "role_score": role_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "semantic_score": semantic_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
        "explanation": explanation,
    }
