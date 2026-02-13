from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for BRD-compliant audit logs"""
    list_display = ['user_id', 'action_type', 'timestamp', 'ip_address']
    list_filter = ['action_type', 'timestamp', 'user_id']
    search_fields = ['user_id__full_name', 'user_id__email', 'action_type', 'ip_address']
    readonly_fields = ['log_id', 'user_id', 'action_type', 'timestamp', 'ip_address']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        """Audit logs should not be manually added"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Audit logs should not be deleted for compliance"""
        return False

    def has_change_permission(self, request, obj=None):
        """Audit logs should not be edited for immutability"""
        return False
