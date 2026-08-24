from django.db import models
from django.conf import settings
import uuid
from .validators import validate_resume_file

class Resume(models.Model):
    STATUS_CHOICES = (
        ('uploaded', 'Uploaded'),
        ('parsing', 'Parsing'),
        ('parsed', 'Parsed'),
        ('failed', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes',
        null=True,
        blank=True,
        help_text="User who uploaded this resume"
    )
    file = models.FileField(upload_to='resumes/', validators=[validate_resume_file])
    original_filename = models.CharField(max_length=255)
    parsed_text = models.TextField(blank=True, default='')
    candidate_profile = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume: {self.original_filename} ({self.status})"

