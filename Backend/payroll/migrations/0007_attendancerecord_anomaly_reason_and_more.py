# Backend\payroll\migrations\0007_attendancerecord_anomaly_reason_and_more.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0006_alter_attendancerecord_break_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancerecord',
            name='anomaly_reason',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='attendancerecord',
            name='is_anomaly',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='attendancerecord',
            name='status',
            field=models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('half_day', 'Half Day'), ('holiday', 'Holiday'), ('weekend', 'Weekend'), ('missing_punch', 'Missing Punch')], max_length=20),
        ),
    ]
