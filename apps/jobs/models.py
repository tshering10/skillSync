import uuid
from django.db import models
from django.conf import settings

class JobDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_descriptions',
        null=True,
        blank=True,
        help_text="User/Recruiter who posted this job"
    )
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, default='')
    raw_text = models.TextField()
    job_profile = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company}" if self.company else self.title
