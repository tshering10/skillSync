from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import JobDescription
from .serializers import JobDescriptionSerializer
from apps.matching.services import extract_job_profile

class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all().order_by('-created_at')
    serializer_class = JobDescriptionSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        
        # 1. Extract full job requirements profile (skills, experience, roles, education)
        raw_text = serializer.validated_data.get('raw_text', '')
        title = serializer.validated_data.get('title', '')
        job_profile = extract_job_profile(raw_text, title=title)
        
        # 2. Save job with user association and rich job_profile
        serializer.save(
            user=user,
            job_profile=job_profile
        )
