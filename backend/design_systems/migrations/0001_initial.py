# Generated manually to add DesignSystem table so that dependent apps can migrate.
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("teams", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="DesignSystem",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="design_systems",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="design_systems",
                        to="teams.Team",
                        null=True,
                        blank=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("version", models.CharField(max_length=50, default="1.0.0")),
                (
                    "logo",
                    models.ImageField(
                        upload_to="design_system_logos/", null=True, blank=True
                    ),
                ),
                (
                    "favicon",
                    models.ImageField(
                        upload_to="design_system_favicons/", null=True, blank=True
                    ),
                ),
                ("is_public", models.BooleanField(default=False)),
                ("auto_sync", models.BooleanField(default=True)),
                ("figma_file_key", models.CharField(max_length=255, blank=True)),
                ("storybook_url", models.URLField(blank=True)),
                ("tags", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-updated_at"],
                "verbose_name": "Design System",
                "verbose_name_plural": "Design Systems",
            },
        ),
    ]
