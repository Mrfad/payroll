# Backend\attendance\urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceRecordViewSet,
    BreakPolicyViewSet,
    LeaveBalanceViewSet,
    LeaveRequestViewSet,
    LeaveTypeViewSet,
    OvertimePolicyViewSet,
    ShiftAssignmentViewSet,
    ShiftViewSet,
)

router = DefaultRouter()
router.register(r"shifts", ShiftViewSet)
router.register(r"break-policies", BreakPolicyViewSet)
router.register(r"overtime-policies", OvertimePolicyViewSet)
router.register(r"shift-assignments", ShiftAssignmentViewSet)
router.register(r"attendance-records", AttendanceRecordViewSet)
router.register(r"leave-types", LeaveTypeViewSet)
router.register(r"leave-balances", LeaveBalanceViewSet)
router.register(r"leave-requests", LeaveRequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
