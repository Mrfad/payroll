# Backend\device\models.py
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class DeviceConfiguration(TimeStampedModel):
    """
    Stores configuration and connection details for physical biometric attendance devices.
    Used to establish connections, fetch logs, or accept webhooks from hardware devices.
    """

    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)  # e.g., 'zkteco_k30', 'faceapi_v2'
    api_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    api_endpoint = models.URLField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    port = models.PositiveIntegerField(blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    auth_credentials = models.JSONField(
        default=dict, blank=True
    )  # {"username":"...", "password":"..."} or token
    fetch_schedule = models.CharField(
        max_length=50, default="*/15 * * * *"
    )  # cron expression
    is_active = models.BooleanField(default=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    extra_config = models.JSONField(
        default=dict, blank=True
    )  # device-specific settings

    def __str__(self):
        return f"{self.name} ({self.device_type})"


class RawAttendanceLog(TimeStampedModel):
    """
    Represents an unprocessed, raw punch log directly from an attendance device.
    These logs are stored immutably before being processed into structured AttendanceRecords.
    """

    device = models.ForeignKey(DeviceConfiguration, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=255)  # employee ID from device
    punch_time = models.DateTimeField()
    direction = models.CharField(
        max_length=10, choices=[("in", "In"), ("out", "Out")], null=True
    )
    raw_data = models.JSONField()  # full device payload
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("processed", "Processed"),
            ("failed", "Failed"),
        ],
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    attendance_record = models.ForeignKey(
        "attendance.AttendanceRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="raw_logs",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["device", "external_id", "punch_time"], name="unique_punch"
            )
        ]

    def __str__(self):
        return f"{self.external_id} - {self.punch_time} ({self.status})"
