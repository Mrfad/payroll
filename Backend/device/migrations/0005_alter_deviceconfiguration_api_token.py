# Backend\device\migrations\0005_alter_deviceconfiguration_api_token.py
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0004_deviceconfiguration_api_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceconfiguration',
            name='api_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
