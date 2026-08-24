from django.contrib import admin
from .models import MatchResult


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('match_score_display', 'role_score_display', 'skill_score_display', 'semantic_score_display', 'resume_filename', 'job_title', 'matched_count', 'missing_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('resume__original_filename', 'job_description__title', 'job_description__company')
    readonly_fields = ('id', 'resume', 'job_description', 'match_score', 'role_score', 'skill_score', 'semantic_score', 'experience_score', 'matched_skills', 'missing_skills', 'recommendations', 'explanation', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Match Pair', {'fields': ('id', 'resume', 'job_description')}),
        ('Scores Breakdown', {'fields': ('match_score', 'role_score', 'skill_score', 'experience_score', 'semantic_score')}),
        ('Skill Analysis', {'fields': ('matched_skills', 'missing_skills')}),
        ('Insights & Recommendations', {'fields': ('explanation', 'recommendations')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def match_score_display(self, obj):
        return f"{obj.match_score:.1f}%"
    match_score_display.short_description = 'Overall Score'
    match_score_display.admin_order_field = 'match_score'

    def role_score_display(self, obj):
        return f"{obj.role_score:.1f}%"
    role_score_display.short_description = 'Role'

    def skill_score_display(self, obj):
        return f"{obj.skill_score:.1f}%"
    skill_score_display.short_description = 'Skill'

    def semantic_score_display(self, obj):
        return f"{obj.semantic_score:.1f}%"
    semantic_score_display.short_description = 'Semantic'

    def resume_filename(self, obj):
        return obj.resume.original_filename
    resume_filename.short_description = 'Resume'

    def job_title(self, obj):
        return str(obj.job_description)
    job_title.short_description = 'Job'

    def matched_count(self, obj):
        return len(obj.matched_skills) if obj.matched_skills else 0
    matched_count.short_description = '✅ Matched'

    def missing_count(self, obj):
        return len(obj.missing_skills) if obj.missing_skills else 0
    missing_count.short_description = '❌ Missing'
