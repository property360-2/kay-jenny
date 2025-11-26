from django.db import models
from django.conf import settings

class AuditTrail(models.Model):
    """Audit trail model for logging all system actions"""

    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('ARCHIVE', 'Archive'),
        ('RESTORE', 'Restore'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    description = models.TextField()
    data_snapshot = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'record_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.model_name} #{self.record_id}"


class Archive(models.Model):
    """Archive model for storing deleted/archived records"""

    model_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    data = models.JSONField()
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='archived_records'
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'record_id']),
        ]

    def __str__(self):
        return f"Archived {self.model_name} #{self.record_id}"
