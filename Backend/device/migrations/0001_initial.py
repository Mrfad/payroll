# Backend\device\migrations\0001_initial.py
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('device_type', models.CharField(max_length=50)),
                ('api_endpoint', models.URLField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('port', models.PositiveIntegerField(blank=True, null=True)),
                ('serial_number', models.CharField(blank=True, max_length=100, null=True)),
                ('auth_credentials', models.JSONField(blank=True, default=dict)),
                ('fetch_schedule', models.CharField(default='*/15 * * * *', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('last_sync_time', models.DateTimeField(blank=True, null=True)),
                ('extra_config', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RawAttendanceLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('external_id', models.CharField(max_length=255)),
                ('punch_time', models.DateTimeField()),
                ('direction', models.CharField(choices=[('in', 'In'), ('out', 'Out')], max_length=10, null=True)),
                ('raw_data', models.JSONField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processed', 'Processed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
