from rest_framework import serializers
from .models import Resume
from .validators import validate_resume_file

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'file', 'original_filename', 'parsed_text', 'extracted_skills', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'parsed_text', 'extracted_skills', 'status', 'created_at', 'updated_at']

class ResumeUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_resume_file])

    class Meta:
        model = Resume
        fields = ['file']
