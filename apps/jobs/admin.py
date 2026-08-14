from django.contrib import admin
from .models import JobDescription


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'skill_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'company', 'raw_text')
    readonly_fields = ('id', 'extracted_skills', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Job Info', {'fields': ('id', 'title', 'company')}),
        ('Content', {'fields': ('raw_text', 'extracted_skills')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def skill_count(self, obj):
        return len(obj.extracted_skills) if obj.extracted_skills else 0
    skill_count.short_description = '# Skills'
