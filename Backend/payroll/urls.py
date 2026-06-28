# Backend\payroll\urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardViewSet,
    EmployeeSalaryStructureViewSet,
    PayrollEntryViewSet,
    PayrollPeriodViewSet,
    PayrollRunViewSet,
    SalaryComponentViewSet,
)

router = DefaultRouter()
router.register(r"salary-components", SalaryComponentViewSet)
router.register(r"employee-salary-structures", EmployeeSalaryStructureViewSet)
router.register(r"payroll-periods", PayrollPeriodViewSet)
router.register(r"payroll-runs", PayrollRunViewSet)
router.register(r"payroll-entries", PayrollEntryViewSet)
router.register(r"dashboard", DashboardViewSet, basename="dashboard")

urlpatterns = [
    path("", include(router.urls)),
]
