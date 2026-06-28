# Backend\companies\models.py
from common.models import TimeStampedModel
from django.db import models


class Company(TimeStampedModel):
    """
    Represents a tenant or organization within the platform.
    All other entities (employees, departments, etc.) are linked to a Company to ensure data isolation.
    """

    name = models.CharField(max_length=255)

    class Meta:
        db_table = "payroll_company"

    def __str__(self):
        return self.name


class Branch(TimeStampedModel):
    """
    Represents a physical location or subsidiary of a Company.
    Useful for organizations with multiple offices or distinct regional entities.
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="branches"
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "companies_branch"
        unique_together = [("company", "name")]

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class Department(TimeStampedModel):
    """
    Represents a functional division within a Company (e.g., HR, IT, Finance).
    Employees are assigned to departments for organizational structuring.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments",
    )
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "payroll_department"
        unique_together = [("company", "name")]

    def __str__(self):
        return self.name
