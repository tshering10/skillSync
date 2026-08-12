from rest_framework import serializers
from .models import MatchResult

class MatchRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField()
    job_description_id = serializers.UUIDField()

class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = ['id', 'resume', 'job_description', 'match_score', 'matched_skills', 'missing_skills', 'explanation', 'created_at']
        read_only_fields = ['id', 'match_score', 'matched_skills', 'missing_skills', 'explanation', 'created_at']
