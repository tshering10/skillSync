from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'full_name', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('-created_at',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Profile Info', {'fields': ('full_name', 'role')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Extra Profile Info', {'fields': ('email', 'full_name', 'role')}),
    )
