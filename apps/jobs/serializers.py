from rest_framework import serializers
from .models import JobDescription

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['id', 'user', 'title', 'company', 'raw_text', 'job_profile', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'job_profile', 'created_at', 'updated_at']
