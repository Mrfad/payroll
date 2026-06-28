# Backend\companies\migrations\0001_initial.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payroll", "0010_remove_auditlog_performed_by_and_more"),
    ]

    operations = [
        # 1. State-only creation of Company (since payroll_company table already exists)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Company",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("name", models.CharField(max_length=255)),
                    ],
                    options={
                        "db_table": "payroll_company",
                    },
                ),
            ],
        ),
        # 2. Database and State creation of Branch (new table)
        migrations.CreateModel(
            name="Branch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("location", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="branches",
                        to="companies.Company",
                    ),
                ),
            ],
            options={
                "db_table": "companies_branch",
                "unique_together": {("company", "name")},
            },
        ),
        # 3. State-only creation of Department (since payroll_department table already exists)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Department",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("name", models.CharField(max_length=255)),
                        (
                            "company",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                to="companies.Company",
                            ),
                        ),
                        (
                            "parent",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.SET_NULL,
                                to="companies.Department",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "payroll_department",
                        "unique_together": {("company", "name")},
                    },
                ),
            ],
        ),
        # 4. Add branch to Department (since it's a new field, we alter the database table payroll_department)
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE payroll_department ADD COLUMN IF NOT EXISTS branch_id bigint NULL REFERENCES companies_branch(id) ON DELETE SET NULL;",
                    reverse_sql="ALTER TABLE payroll_department DROP COLUMN IF EXISTS branch_id;",
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="department",
                    name="branch",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="departments",
                        to="companies.Branch",
                    ),
                ),
            ],
        ),
    ]
