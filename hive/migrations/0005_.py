import os

from django.db import migrations

class Migration(migrations.Migration):
    schema_name = os.getenv('STORAGE_SCHEMA')
    dependencies = [
        ('hive', '0004_'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "CREATE SCHEMA %s;" % schema_name,
            ],
            reverse_sql=[
                "DROP SCHEMA %s CASCADE;" % schema_name,
            ]
        ),
    ]