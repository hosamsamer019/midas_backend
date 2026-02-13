from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AuditLog(models.Model):
    """Extended audit log as per BRD specification"""
    log_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='user_id')
    action_type = models.CharField(max_length=100)  # e.g., 'login', 'logout', 'create_user', 'upload_data', etc.
    action_details = models.TextField(null=True, blank=True)  # Additional details about the action
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)  # Browser/client user agent
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'audit_auditlog'
        ordering = ['-timestamp']

    def __str__(self):
        user_name = self.user_id.full_name if self.user_id else "Unknown User"
        return f"{user_name} - {self.action_type} at {self.timestamp}"
