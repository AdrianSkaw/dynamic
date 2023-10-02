import os
import pathlib

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import migrations
from dotenv import load_dotenv

project_dir = pathlib.Path(__file__).parent.resolve().parent.parent
env_file = project_dir / '.env'
load_dotenv(env_file)


def create_test_user(apps, schema_editor):
    # Create a new user

    user_name = os.getenv('HIVE_USER')
    password = os.getenv('HIVE_PASS')

    user = User(username=user_name, password=make_password(password))
    user.save()


class Migration(migrations.Migration):
    dependencies = [
        ('hive', '0002_'),
    ]

    operations = [
        migrations.RunPython(create_test_user),
    ]
