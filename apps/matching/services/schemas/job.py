from typing import List
from pydantic import BaseModel, Field
from .common import EducationItem, SkillGroup


class JobProfileSchema(BaseModel):
    required_skills: List[str] = Field(
        description="Mandatory, core technical skills that the candidate MUST possess"
    )
    preferred_skills: List[str] = Field(
        description="Nice-to-have, bonus, or preferred skills that are not strictly mandatory"
    )
    skill_groups: List[SkillGroup] = Field(
        description="Alternative skill groups where candidate only needs ONE of the options, e.g. AWS or GCP or Azure"
    )
    required_experience_years: float = Field(
        description="Minimum years of professional experience required by the job (0.0 if not specified)"
    )
    roles: List[str] = Field(
        description="Job role titles, e.g. ['Senior Python Developer']"
    )
    education: List[EducationItem] = Field(
        description="Required or preferred degrees specified by the job description"
    )
