# Backend\payroll\migrations\0002_alter_attendancerecord_options_and_more.py
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendancerecord',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='breakpolicy',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='employeesalarystructure',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='leavebalance',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='leaverequest',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='leavetype',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='overtimepolicy',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='payrollentry',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='payrollperiod',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='payrollrun',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='salarycomponent',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='shift',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='shiftassignment',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='employee',
            name='employee_id',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
