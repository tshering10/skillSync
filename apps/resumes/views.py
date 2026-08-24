from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Resume
from .serializers import ResumeSerializer, ResumeUploadSerializer
from .parsers import parse_resume_file
from apps.matching.services import extract_skills_from_text

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all().order_by('-created_at')
    serializer_class = ResumeSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.action == 'create':
            return ResumeUploadSerializer
        return ResumeSerializer

    def perform_create(self, serializer):
        uploaded_file = serializer.validated_data['file']
        user = self.request.user if self.request.user.is_authenticated else None
        resume = serializer.save(
            user=user,
            original_filename=uploaded_file.name,
            status='parsing'
        )

        try:
            # Parse text
            raw_text = parse_resume_file(resume.file.path)
            resume.parsed_text = raw_text

            # Extract skills using spaCy
            skills = extract_skills_from_text(raw_text)
            resume.extracted_skills = skills
            resume.status = 'parsed'
            resume.save()

        except Exception as e:
            resume.status = 'failed'
            resume.save()
            raise serializers.ValidationError({
                "error": f"Failed to parse resume: {str(e)}",
                "resume_id": str(resume.id)
            })

    def create(self, request, *args, **kwargs):
        upload_serializer = self.get_serializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        self.perform_create(upload_serializer)
        
        # Return the full Resume representation in response
        resume_instance = upload_serializer.instance
        headers = self.get_success_headers(upload_serializer.data)
        return Response(
            ResumeSerializer(resume_instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
