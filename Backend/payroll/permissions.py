# Backend\payroll\permissions.py
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to view or edit it.
    Assumes the model has an `employee` field.
    """

    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user and request.user.is_staff:
            return True

        # Check if the object belongs to the requesting user's employee profile
        # Some objects might be the Employee itself, others might have an `employee` foreign key.
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "employee"):
            return obj.employee.user == request.user

        return False


class IsManagerOrDeveloper(permissions.BasePermission):
    """
    Allows access only to users in the Managers or Developers groups, or admins.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return request.user.groups.filter(name__in=["Managers", "Developers"]).exists()
