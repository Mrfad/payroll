# Backend\device\migrations\0006_rawattendancelog_attendance_record.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0005_alter_deviceconfiguration_api_token'),
        ('payroll', '0008_remove_attendancerecord_raw_logs'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawattendancelog',
            name='attendance_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='raw_logs', to='payroll.attendancerecord'),
        ),
    ]
