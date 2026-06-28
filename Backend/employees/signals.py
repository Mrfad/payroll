# Backend\employees\signals.py
from accounts.models import UserProfile
from asgiref.sync import async_to_sync
from attendance.models import (
    AttendanceRecord,
    BreakPolicy,
    LeaveBalance,
    LeaveRequest,
    LeaveType,
    OvertimePolicy,
    Shift,
    ShiftAssignment,
)
from audit.models import AuditLog
from channels.layers import get_channel_layer
from companies.models import Company, Department
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save, pre_save
from payroll.models import (
    EmployeeSalaryStructure,
    PayrollEntry,
    PayrollPeriod,
    PayrollRun,
    SalaryComponent,
)

from employees.models import Employee

from .middleware import get_current_user, get_request_source

# IMPORTANT: Do not include AuditLog in MODELS_TO_WATCH to prevent infinite recursion
MODELS_TO_WATCH = [
    Employee,
    Shift,
    BreakPolicy,
    OvertimePolicy,
    ShiftAssignment,
    AttendanceRecord,
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    SalaryComponent,
    EmployeeSalaryStructure,
    PayrollPeriod,
    PayrollRun,
    PayrollEntry,
    Company,
    Department,
]


def broadcast_update(model_name, action):
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            "payroll_updates",
            {"type": "data_update", "model": model_name, "action": action},
        )


def _create_audit_log(sender, instance, action_name, changes=None):
    # Retrieve the user from the thread-local middleware
    performed_by = get_current_user()
    if performed_by and not performed_by.is_authenticated:
        performed_by = None

    target_user = None
    if hasattr(instance, "user") and getattr(instance, "user_id", None):
        target_user = instance.user
    elif sender.__name__ == "User":
        target_user = instance

    # Prevent IntegrityError on cascading deletes from User.
    # If the user is being deleted, any new AuditLog pointing to them will cause a DB constraint failure at commit.
    if action_name == "HARD_DELETE" and sender.__name__ in [
        "Employee",
        "Company",
        "User",
    ]:
        target_user = None

    source = get_request_source()
    details = f"[{source}] {action_name.title()} {sender.__name__} {getattr(instance, 'pk', '')}"
    if sender.__name__ == "Employee":
        details += f" ({getattr(instance, 'employee_id', '')})"

    if changes:
        details += ". Changes: " + "; ".join(changes)

    # Don't create an audit log if we are creating an audit log
    AuditLog.objects.create(
        action=action_name,
        target_user=target_user,
        performed_by=performed_by,
        details=details,
    )
    broadcast_update(sender.__name__, action_name.lower())


def model_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            changes = []
            for field in instance._meta.fields:
                field_name = field.name
                old_val = getattr(old_instance, field_name)
                new_val = getattr(instance, field_name)
                if old_val != new_val:
                    changes.append(
                        f"{field_name} changed from '{old_val}' to '{new_val}'"
                    )

            instance._audit_changes = changes

            # Advanced Action Detection for Employee
            if sender.__name__ == "Employee":
                old_deleted = getattr(old_instance, "deleted_at", None)
                new_deleted = getattr(instance, "deleted_at", None)
                old_active = getattr(old_instance, "is_active", None)
                new_active = getattr(instance, "is_active", None)

                if old_deleted is None and new_deleted is not None:
                    instance._audit_action = "SOFT_DELETE"
                elif old_deleted is not None and new_deleted is None:
                    instance._audit_action = "RESTORE"
                elif old_active and not new_active:
                    instance._audit_action = "FREEZE"
                elif not old_active and new_active:
                    instance._audit_action = "UNFREEZE"

        except sender.DoesNotExist:
            instance._audit_changes = []
    else:
        instance._audit_changes = []


def model_saved(sender, instance, created, **kwargs):
    action_name = getattr(instance, "_audit_action", "CREATE" if created else "UPDATE")
    changes = getattr(instance, "_audit_changes", [])

    _create_audit_log(sender, instance, action_name, changes)
    broadcast_update(sender.__name__, "create" if created else "update")


def model_deleted(sender, instance, **kwargs):
    _create_audit_log(sender, instance, "HARD_DELETE", [])
    broadcast_update(sender.__name__, "delete")


for model in MODELS_TO_WATCH:
    pre_save.connect(model_pre_save, sender=model)
    post_save.connect(model_saved, sender=model)
    post_delete.connect(model_deleted, sender=model)


# Missing signals added for coverage matrix
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


def sync_active_status(sender, instance, **kwargs):
    if instance.user and hasattr(instance, "is_active"):
        if instance.user.is_active != instance.is_active:
            instance.user.is_active = instance.is_active
            instance.user.save(update_fields=["is_active"])


post_save.connect(sync_active_status, sender=Employee)
