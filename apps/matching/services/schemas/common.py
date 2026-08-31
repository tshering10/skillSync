from typing import List, Optional
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    degree_level: str = Field(
        description="Normalized degree level: 'Doctorate', 'Master', 'Bachelor', 'Associate/Diploma', or 'Other'"
    )
    field_of_study: str = Field(
        description="Normalized major/field of study, e.g. 'Computer Science', 'Software Engineering', 'Information Technology', 'Data Science', 'General'"
    )
    raw_degree: str = Field(
        description="Exact degree string from the text, e.g. 'Bachelor of Science in CS'"
    )
    hierarchy_rank: int = Field(
        description="Hierarchy rank: Doctorate=4, Master=3, Bachelor=2, Associate/Diploma=1, Other=0"
    )


class SkillGroup(BaseModel):
    type: str = Field(
        default="one_of",
        description="Constraint type, almost always 'one_of'"
    )
    skills: List[str] = Field(
        description="Alternative skills where having ANY ONE satisfies the requirement, e.g. ['Node.js', 'Go', 'Java', 'Python']"
    )
    raw_clause: Optional[str] = Field(
        default="",
        description="Original sentence/clause from the JD describing the alternative requirement"
    )
