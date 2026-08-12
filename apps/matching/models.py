import uuid
from django.db import models
from apps.resumes.models import Resume
from apps.jobs.models import JobDescription

class MatchResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='match_results')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='match_results')
    match_score = models.FloatField()
    matched_skills = models.JSONField(default=dict)
    missing_skills = models.JSONField(default=dict)
    explanation = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.match_score:.1f}% (Resume {self.resume.id} <-> Job {self.job_description.id})"
