from rest_framework import viewsets, status
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

    def create(self, request, *args, **kwargs):
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['file']
        resume = serializer.save(
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

            return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            resume.status = 'failed'
            resume.save()
            return Response(
                {"error": f"Failed to parse resume: {str(e)}", "resume_id": str(resume.id)},
                status=status.HTTP_400_BAD_REQUEST
            )
