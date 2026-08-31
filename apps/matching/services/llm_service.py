import os
import json
import logging
from google import genai
from google.genai import types
from django.conf import settings

from .schemas import (
    EducationItem,
    SkillGroup,
    CandidateProfileSchema,
    JobProfileSchema,
)

logger = logging.getLogger(__name__)


# GEMINI CLIENT INITIALIZATION

def get_genai_client():
    """Initialize and return the Gemini GenAI client."""
    api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set. LLM extraction will fail or need fallback.")
        return None
    return genai.Client(api_key=api_key)

# LLM EXTRACTION FUNCTIONS

def extract_candidate_profile_llm(parsed_text: str) -> dict:
    """
    Extract structured candidate profile from resume text using Gemini + Pydantic.
    """
    if not parsed_text or not parsed_text.strip():
        return {
            "skills": [],
            "roles": [],
            "experience_years": 0.0,
            "education": [],
            "education_details": [],
        }

    client = get_genai_client()
    if not client:
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in .env.")

    model_name = getattr(settings, "GEMINI_MODEL_NAME", "gemini-2.5-flash")

    prompt = f"""You are an expert HR Tech AI. Analyze the following candidate resume text and extract structured profile data.

Instructions:
1. Technical Skills: Extract canonical, specific technical skills (e.g. Python, Django, PostgreSQL, Docker, AWS). Standardize aliases (e.g. JS -> JavaScript, ReactJS -> React).
2. Work Experience: Calculate the true cumulative professional years of experience from employment dates.
3. Roles: Identify primary job titles/roles held by the candidate.
4. Education: Extract all degrees, normalize degree level (Doctorate/Master/Bachelor/Associate/Other), and assign hierarchy rank (4 to 0).

Resume Content:
---
{parsed_text}
---
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CandidateProfileSchema,
                temperature=0.1,
            ),
        )

        parsed_data = json.loads(response.text)

        # Structure response to be 100% compatible with matching.py & Resume model
        return {
            "skills": parsed_data.get("skills", []),
            "roles": parsed_data.get("roles", []),
            "experience_years": float(parsed_data.get("experience_years", 0.0)),
            "education": [e.get("raw_degree") for e in parsed_data.get("education", [])],
            "education_details": parsed_data.get("education", []),
        }

    except Exception as e:
        logger.error(f"Gemini candidate extraction failed: {e}")
        raise e


def extract_job_profile_llm(parsed_text: str, title: str = "") -> dict:
    """
    Extract structured job profile from JD text using Gemini + Pydantic.
    """
    if not parsed_text or not parsed_text.strip():
        return {
            "skills": [],
            "required_skills": [],
            "preferred_skills": [],
            "skill_groups": [],
            "required_experience_years": 0.0,
            "roles": [title.strip().title()] if title else [],
            "education": [],
            "education_details": [],
        }

    client = get_genai_client()
    if not client:
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in .env.")

    model_name = getattr(settings, "GEMINI_MODEL_NAME", "gemini-2.5-flash")

    prompt = f"""You are an expert HR Tech AI. Analyze the following Job Description (JD) and extract structured requirement data.

Job Title: {title}

Instructions:
1. Required vs Preferred Skills:
   - required_skills: Strictly mandatory must-have skills.
   - preferred_skills: Nice-to-have, bonus, or optional skills.
2. Skill Groups (Alternatives / OR Logic):
   - Whenever the JD expresses alternative options like "Node.js, Go, Java, or Python" or "AWS or Azure", create a skill_group with type="one_of" and list the alternative skills.
3. Experience:
   - Extract minimum required years of experience (e.g. "3+ years" -> 3.0, "3-5 years" -> 3.0, none mentioned -> 0.0).
4. Education:
   - Extract degree requirements (degree level, hierarchy rank, field of study).

Job Description Content:
---
{parsed_text}
---
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobProfileSchema,
                temperature=0.1,
            ),
        )

        parsed_data = json.loads(response.text)

        req_skills = parsed_data.get("required_skills", [])
        pref_skills = parsed_data.get("preferred_skills", [])
        all_skills = sorted(list(set(req_skills + pref_skills)))

        roles = parsed_data.get("roles", [])
        if title and title.strip():
            roles = [title.strip().title()] + [r for r in roles if r.lower() != title.strip().lower()]

        return {
            "skills": all_skills,
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "skill_groups": parsed_data.get("skill_groups", []),
            "required_experience_years": float(parsed_data.get("required_experience_years", 0.0)),
            "roles": roles,
            "education": [e.get("raw_degree") for e in parsed_data.get("education", [])],
            "education_details": parsed_data.get("education", []),
        }

    except Exception as e:
        logger.error(f"Gemini job extraction failed: {e}")
        raise e

# OPTIONAL: NATURAL LANGUAGE MATCH EXPLANATION

def generate_match_explanation_llm(match_data: dict, candidate_profile: dict, job_profile: dict) -> str:
    """
    Generate an insightful natural language match explanation and advice using Gemini.
    """
    client = get_genai_client()
    if not client:
        return match_data.get("explanation", "")

    model_name = getattr(settings, "GEMINI_MODEL_NAME", "gemini-2.5-flash")

    prompt = f"""You are a senior technical recruiter and career advisor.
Given the following resume-to-job match results, write a concise, professional, 2-3 sentence summary explaining why this score was achieved and what the candidate can do to improve.

Match Score: {match_data.get('match_score')}%
Skill Score: {match_data.get('skill_score')}%
Experience Score: {match_data.get('experience_score')}%
Role Score: {match_data.get('role_score')}%
Matched Skills: {list(match_data.get('matched_skills', {}).keys())}
Missing Skills: {list(match_data.get('missing_skills', {}).keys())}
Candidate Experience: {candidate_profile.get('experience_years', 0)} years
Job Required Experience: {job_profile.get('required_experience_years', 0)} years

Keep the feedback constructive, specific, and directly relevant to the gaps.
"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        return response.text.strip()
    except Exception:
        return match_data.get("explanation", "")
