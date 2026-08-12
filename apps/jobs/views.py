from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import JobDescription
from .serializers import JobDescriptionSerializer
from apps.matching.services import extract_skills_from_text

class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all().order_by('-created_at')
    serializer_class = JobDescriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        job = serializer.save()

        # Extract skills from job description text
        skills = extract_skills_from_text(job.raw_text)
        job.extracted_skills = skills
        job.save()

        return Response(JobDescriptionSerializer(job).data, status=status.HTTP_201_CREATED)
