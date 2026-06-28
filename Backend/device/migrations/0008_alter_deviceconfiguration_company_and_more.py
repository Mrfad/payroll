# Backend\device\migrations\0008_alter_deviceconfiguration_company_and_more.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        ('device', '0007_alter_rawattendancelog_options_and_more'),
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceconfiguration',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.company'),
        ),
        migrations.AlterField(
            model_name='rawattendancelog',
            name='attendance_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='raw_logs', to='attendance.attendancerecord'),
        ),
    ]
