from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AuditLog(models.Model):
    """Comprehensive audit trail for all model changes"""

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
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action (null for system actions)"
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    model_name = models.CharField(max_length=100, db_index=True)
    record_id = models.IntegerField(db_index=True)
    description = models.TextField(blank=True)

    data_before = models.JSONField(null=True, blank=True, help_text="State before the change (for UPDATE/DELETE)")
    data_after = models.JSONField(null=True, blank=True, help_text="State after the change (for CREATE/UPDATE)")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['model_name', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.action} - {self.model_name} #{self.record_id}"

    @property
    def changes_summary(self):
        """Generate summary of what changed for UPDATE actions"""
        if self.action != 'UPDATE' or not self.data_before or not self.data_after:
            return None

        changes = []
        for key in self.data_after.keys():
            if key in self.data_before:
                old_val = self.data_before[key]
                new_val = self.data_after[key]
                if old_val != new_val:
                    changes.append(f"{key}: {old_val} → {new_val}")

        return changes if changes else None
