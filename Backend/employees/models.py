# Backend\employees\models.py
import uuid
from django.utils import timezone
from common.models import TimeStampedModel
from companies.models import Branch, Company, Department
from django.conf import settings
from django.db import models


class Employee(TimeStampedModel):
    """
    The central entity of the system representing a person working for a Company.
    Stores personal information, employment details, and serves as the anchor for payroll and attendance.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    employee_id = models.CharField(max_length=50, unique=True, blank=True)
    device_user_ids = models.JSONField(default=dict, blank=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="employee_profiles/", blank=True, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True, help_text="Date of joining")   # NEW

    class Meta:
        db_table = "payroll_employee"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        if self.device_user_ids is None:
            self.device_user_ids = {}
        # NEW: If hire_date is not set and this is a new employee, set to today
        if not self.hire_date and not self.pk:
            self.hire_date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.employee_id})"
