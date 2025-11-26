from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'is_archived', 'created_at']
    list_filter = ['role', 'is_active', 'is_archived', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Status', {'fields': ('role', 'phone', 'is_archived')}),
    )
