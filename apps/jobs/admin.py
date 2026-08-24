from django.contrib import admin
from .models import JobDescription


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'user', 'skill_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'company', 'raw_text', 'user__email')
    readonly_fields = ('id', 'job_profile', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Job Info', {'fields': ('id', 'user', 'title', 'company')}),
        ('Content', {'fields': ('raw_text', 'job_profile')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def skill_count(self, obj):
        skills = obj.job_profile.get('skills', []) if isinstance(obj.job_profile, dict) else []
        return len(skills)
    skill_count.short_description = '# Skills'
