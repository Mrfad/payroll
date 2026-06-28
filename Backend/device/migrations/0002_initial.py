# Backend\device\migrations\0002_initial.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('device', '0001_initial'),
        ('payroll', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceconfiguration',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company'),
        ),
        migrations.AddField(
            model_name='rawattendancelog',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='device.deviceconfiguration'),
        ),
    ]
