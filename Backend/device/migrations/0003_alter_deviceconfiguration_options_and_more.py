# Backend\device\migrations\0003_alter_deviceconfiguration_options_and_more.py
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deviceconfiguration',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='rawattendancelog',
            options={'ordering': ['-created_at']},
        ),
    ]
