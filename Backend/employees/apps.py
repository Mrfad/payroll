# Backend\employees\apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group

    Group.objects.get_or_create(name="Employee")
    Group.objects.get_or_create(name="Managers")
    Group.objects.get_or_create(name="Developers")


class EmployeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "employees"

    def ready(self):
        import employees.signals

        post_migrate.connect(create_default_groups, sender=self)
