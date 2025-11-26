from django.contrib import admin
from .models import AuditTrail, Archive

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'record_id', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'model_name', 'description']
    readonly_fields = ['user', 'action', 'model_name', 'record_id', 'description', 'data_snapshot', 'ip_address', 'created_at']

    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys"""
        return super().get_queryset(request).select_related('user')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'record_id', 'archived_by', 'created_at']
    list_filter = ['model_name', 'created_at']
    search_fields = ['model_name', 'archived_by__username']
    readonly_fields = ['model_name', 'record_id', 'data', 'archived_by', 'reason', 'created_at']

    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys"""
        return super().get_queryset(request).select_related('archived_by')

    def has_add_permission(self, request):
        return False
