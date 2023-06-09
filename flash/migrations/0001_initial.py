# Generated by Django 4.2 on 2023-05-07 09:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Flash",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(max_length=60)),
                ("active", models.BooleanField(default=True)),
                (
                    "uuid",
                    models.CharField(default=uuid.uuid4, max_length=36, unique=True),
                ),
                ("outcome", models.BooleanField(default=None, null=True)),
                ("votes", models.TextField(default="{}")),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
