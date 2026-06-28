# Backend\audit\models.py
from common.models import TimeStampedModel
from django.conf import settings
from django.db import models


class AuditLog(TimeStampedModel):
    """
    Maintains an immutable record of significant actions within the system.
    Tracks who made what changes (create, update, delete) to which records for compliance.
    """

    action = models.CharField(max_length=50)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_targets",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_actions",
    )
    details = models.TextField()

    class Meta:
        db_table = "payroll_auditlog"

    def __str__(self):
        return f"{self.action} on {self.target_user} by {self.performed_by}"
