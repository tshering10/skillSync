from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import JobDescription
from .serializers import JobDescriptionSerializer
from apps.matching.services import extract_skills_from_text

class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all().order_by('-created_at')
    serializer_class = JobDescriptionSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        
        # 1. Extract skills from the raw JD text
        raw_text = serializer.validated_data.get('raw_text', '')
        skills = extract_skills_from_text(raw_text)
        
        # 2. Save job with user association and job_profile
        serializer.save(
            user=user,
            job_profile={
                "skills": skills,
            }
        )
