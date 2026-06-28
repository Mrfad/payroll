# Backend\audit\migrations\0001_initial.py
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=50)),
                ('details', models.TextField()),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_actions', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_targets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payroll_auditlog',
            },
        ),
    ]
