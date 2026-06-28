# Backend\common\models.py
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating `created_at` and `updated_at` fields.
    All other models should inherit from this to ensure consistent timestamp tracking.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
