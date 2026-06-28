# Backend\attendance\migrations\0002_alter_breakpolicy_company_alter_leavetype_company_and_more.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breakpolicy',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AlterField(
            model_name='leavetype',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AlterField(
            model_name='overtimepolicy',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]
