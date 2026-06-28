# Backend\payroll\migrations\0009_alter_department_options_alter_shift_options_and_more.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0008_remove_attendancerecord_raw_logs'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={},
        ),
        migrations.AlterModelOptions(
            name='shift',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='attendancerecord',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together={('company', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='shift',
            unique_together={('company', 'name')},
        ),
        migrations.AddConstraint(
            model_name='attendancerecord',
            constraint=models.UniqueConstraint(fields=('employee', 'date'), name='unique_attendance_per_day'),
        ),
    ]
