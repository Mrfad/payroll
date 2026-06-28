# Backend\payroll\migrations\0006_alter_attendancerecord_break_end_and_more.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0005_alter_attendancerecord_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancerecord',
            name='break_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendancerecord',
            name='break_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendancerecord',
            name='first_in',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendancerecord',
            name='last_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendancerecord',
            name='shift_assignment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.shiftassignment'),
        ),
    ]
