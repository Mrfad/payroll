import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from payroll.models import Company, Department, Employee, UserProfile, AuditLog

@pytest.mark.django_db
class TestSignals:
    def test_audit_log_creation_on_save(self, company, department):
        user = User.objects.create_user(username='sig_user', password='pw')
        AuditLog.objects.all().delete()
        
        emp = Employee.objects.create(user=user, company=company, department=department)
        
        logs = AuditLog.objects.filter(action='CREATE')
        assert logs.count() >= 1
        assert any('Employee' in log.details for log in logs)

    def test_audit_log_creation_on_delete(self, company, department):
        user = User.objects.create_user(username='del_user', password='pw')
        emp = Employee.objects.create(user=user, company=company, department=department)
        AuditLog.objects.all().delete()
        
        emp.delete()
        logs = AuditLog.objects.filter(action='HARD_DELETE')
        assert logs.count() == 1

    def test_audit_log_creation_on_restore_and_soft_delete(self, company, department):
        user = User.objects.create_user(username='soft_user', password='pw')
        emp = Employee.objects.create(user=user, company=company, department=department)
        AuditLog.objects.all().delete()
        
        emp.deleted_at = timezone.now()
        emp.save()
        
        assert AuditLog.objects.filter(action='SOFT_DELETE').exists()
        
        emp.deleted_at = None
        emp.save()
        
        assert AuditLog.objects.filter(action='RESTORE').exists()

    def test_user_profile_auto_creation(self):
        user = User.objects.create_user(username='profile_user', password='pw')
        assert hasattr(user, 'profile')
        assert user.profile is not None

    def test_active_status_sync(self, company, department):
        user = User.objects.create_user(username='active_sync_user', password='pw')
        emp = Employee.objects.create(user=user, company=company, department=department)
        
        emp.is_active = False
        emp.save()
        
        user.refresh_from_db()
        assert user.is_active is False
        
        emp.is_active = True
        emp.save()
        
        user.refresh_from_db()
        assert user.is_active is True

    def test_audit_log_creation_on_user_save(self):
        AuditLog.objects.all().delete()
        user = User.objects.create_user(username='audit_user', password='pw')
        
        # This triggers a save on User model
        user.first_name = "Audited"
        user.save()
        
        logs = AuditLog.objects.filter(target_user=user)
        assert logs.exists()

