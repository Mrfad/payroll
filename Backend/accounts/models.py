# Backend\accounts\models.py
from common.models import TimeStampedModel
from django.conf import settings
from django.db import models


class UserProfile(TimeStampedModel):
    """
    Extends the default Django User model with application-specific preferences and roles.
    Connects authentication details to the core Employee entity.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    theme = models.CharField(
        max_length=20, default="light", choices=[("light", "Light"), ("dark", "Dark")]
    )

    class Meta:
        db_table = "payroll_userprofile"

    def __str__(self):
        return f"{self.user.username}'s Profile"
