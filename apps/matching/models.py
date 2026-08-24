import uuid
from django.db import models
from apps.resumes.models import Resume
from apps.jobs.models import JobDescription

class MatchResult(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='match_results'
    )

    job_description = models.ForeignKey(
        JobDescription,
        on_delete=models.CASCADE,
        related_name='match_results'
    )

    # Overall score
    match_score = models.FloatField(
        help_text="Overall weighted match percentage (0-100)"
    )

    # Component scores
    role_score = models.FloatField(
        default=0.0,
        help_text="Role/title compatibility score (0-100)"
    )

    skill_score = models.FloatField(
        default=0.0,
        help_text="Skill compatibility score (0-100)"
    )

    experience_score = models.FloatField(
        default=0.0,
        help_text="Experience/seniority fit score (0-100)"
    )

    semantic_score = models.FloatField(
        default=0.0,
        help_text="Semantic compatibility score (0-100)"
    )

    # Matching evidence
    matched_skills = models.JSONField(default=dict)
    missing_skills = models.JSONField(default=dict)

    # Generated feedback
    recommendations = models.JSONField(
        default=list,
        blank=True
    )

    explanation = models.TextField(
        blank=True,
        default=''
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"Match: {self.match_score:.1f}% "
            f"(Resume {self.resume.id} <-> "
            f"Job {self.job_description.id})"
        )
