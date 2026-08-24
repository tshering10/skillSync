from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import MatchResult
from .serializers import MatchResultSerializer, MatchRequestSerializer
from apps.resumes.models import Resume
from apps.jobs.models import JobDescription
from .services import calculate_match

class MatchViewSet(viewsets.ModelViewSet):
    queryset = MatchResult.objects.all().order_by('-created_at')
    serializer_class = MatchResultSerializer

    def create(self, request, *args, **kwargs):
        serializer = MatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resume_id = serializer.validated_data['resume_id']
        job_id = serializer.validated_data['job_description_id']

        try:
            resume = Resume.objects.get(id=resume_id)
            job = JobDescription.objects.get(id=job_id)
        except (Resume.DoesNotExist, JobDescription.DoesNotExist):
            return Response({"error": "Resume or Job Description not found."}, status=status.HTTP_404_NOT_FOUND)

        match_data = calculate_match(
            candidate_profile=resume.candidate_profile,
            job_profile=job.job_profile,
            candidate_text=resume.parsed_text,
            job_text=job.raw_text
        )

        match_result = MatchResult.objects.create(
            resume=resume,
            job_description=job,
            match_score=match_data['match_score'],
            role_score=match_data.get('role_score', 0.0),
            skill_score=match_data.get('skill_score', 0.0),
            semantic_score=match_data.get('semantic_score', 0.0),
            experience_score=match_data.get('experience_score', 0.0),
            matched_skills=match_data['matched_skills'],
            missing_skills=match_data['missing_skills'],
            recommendations=match_data.get('recommendations', []),
            explanation=match_data['explanation']
        )

        return Response(MatchResultSerializer(match_result).data, status=status.HTTP_201_CREATED)
