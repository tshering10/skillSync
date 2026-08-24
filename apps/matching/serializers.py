from rest_framework import serializers
from .models import MatchResult

class MatchRequestSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField()
    job_description_id = serializers.UUIDField()

class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = [
            'id', 'resume', 'job_description',
            'match_score', 'role_score', 'skill_score', 'experience_score', 'semantic_score',
            'matched_skills', 'missing_skills', 'recommendations', 'explanation',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'match_score', 'role_score', 'skill_score', 'experience_score', 'semantic_score',
            'matched_skills', 'missing_skills', 'recommendations', 'explanation',
            'created_at', 'updated_at'
        ]
