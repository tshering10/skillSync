from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'status', 'skill_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('original_filename', 'user__email', 'user__full_name', 'parsed_text')
    readonly_fields = ('id', 'parsed_text', 'candidate_profile', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('File Info', {'fields': ('id', 'file', 'original_filename', 'user', 'status')}),
        ('Parsed Content', {'fields': ('parsed_text', 'candidate_profile')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def skill_count(self, obj):
        skills = obj.candidate_profile.get('skills', []) if isinstance(obj.candidate_profile, dict) else []
        return len(skills)
    skill_count.short_description = '# Skills'
