# Backend\device\migrations\0007_alter_rawattendancelog_options_and_more.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0006_rawattendancelog_attendance_record'),
        ('payroll', '0009_alter_department_options_alter_shift_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rawattendancelog',
            options={},
        ),
        migrations.AddConstraint(
            model_name='rawattendancelog',
            constraint=models.UniqueConstraint(fields=('device', 'external_id', 'punch_time'), name='unique_punch'),
        ),
    ]
