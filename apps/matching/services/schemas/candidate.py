from typing import List
from pydantic import BaseModel, Field
from .common import EducationItem


class CandidateProfileSchema(BaseModel):
    skills: List[str] = Field(
        description="All technical skills, frameworks, libraries, databases, cloud tools, and programming languages found in the resume"
    )
    roles: List[str] = Field(
        description="Current or target professional job titles, e.g. ['Senior Backend Engineer', 'Python Developer']"
    )
    experience_years: float = Field(
        description="Total cumulative career experience in years calculated from work history date ranges"
    )
    education: List[EducationItem] = Field(
        description="All educational degrees extracted from the candidate's resume"
    )
