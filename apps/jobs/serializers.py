from rest_framework import serializers
from .models import JobDescription

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['id', 'title', 'company', 'raw_text', 'extracted_skills', 'created_at', 'updated_at']
        read_only_fields = ['id', 'extracted_skills', 'created_at', 'updated_at']
