# Backend\device\migrations\0009_alter_deviceconfiguration_company.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        ('device', '0008_alter_deviceconfiguration_company_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceconfiguration',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]
