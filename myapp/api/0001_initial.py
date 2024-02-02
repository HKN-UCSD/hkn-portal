# Generated by Django 4.2.3 on 2023-10-04 20:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import myapp.api.models.events
import myapp.api.models.users
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "user_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("middle_name", models.CharField(blank=True, max_length=65, null=True)),
                ("pronouns", models.CharField(blank=True, max_length=65, null=True)),
                ("email", models.EmailField(max_length=65, unique=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", myapp.api.models.users.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Event",
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
                ("name", models.CharField(max_length=255)),
                ("time_created", models.DateTimeField(auto_now_add=True)),
                ("time_last_modified", models.DateTimeField(auto_now=True)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("points", models.FloatField(default=1)),
                ("description", models.TextField(blank=True)),
                ("is_draft", models.BooleanField(default=True)),
                (
                    "start_time",
                    models.DateTimeField(
                        blank=True, default=django.utils.timezone.now, null=True
                    ),
                ),
                (
                    "end_time",
                    models.DateTimeField(
                        blank=True, default=django.utils.timezone.now, null=True
                    ),
                ),
                ("anon_viewable", models.BooleanField(default=False)),
            ],
            options={
                "permissions": [
                    ("can_view_draft", "Can view drafts of events"),
                    (
                        "can_view_relevant_users",
                        "Can view all users involved with an event, not just oneself",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="EventType",
            fields=[
                (
                    "name",
                    models.CharField(
                        max_length=255, primary_key=True, serialize=False, unique=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OutreachStudent",
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
                ("car", models.CharField(default="No", max_length=65)),
                ("outreach_course", models.CharField(default="None", max_length=65)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Officer",
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
                ("position", models.CharField(blank=True, max_length=65, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Member",
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
                (
                    "preferred_name",
                    models.CharField(blank=True, max_length=65, null=True),
                ),
                ("major", models.CharField(max_length=65, null=True)),
                ("degree", models.CharField(default="Undergraduate", max_length=65)),
                ("grad_year", models.IntegerField(default=2023)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Inductee",
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
                (
                    "preferred_name",
                    models.CharField(blank=True, max_length=65, null=True),
                ),
                ("major", models.CharField(blank=True, max_length=65, null=True)),
                ("degree", models.CharField(default="Undergraduate", max_length=65)),
                ("grad_year", models.IntegerField(default=2023)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventActionRecord",
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
                ("action_time", models.DateTimeField(auto_now_add=True)),
                (
                    "action",
                    models.TextField(
                        blank=True,
                        choices=[
                            ("RSVP", "RSVP"),
                            ("Sign In", "Sign In"),
                            ("Check Off", "Check Off"),
                        ],
                        null=True,
                    ),
                ),
                ("details", models.TextField(blank=True)),
                ("points", models.FloatField(default=0)),
                (
                    "extra_data",
                    models.JSONField(
                        default=myapp.api.models.events.EventActionRecord.default_extra_data
                    ),
                ),
                (
                    "acted_on",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.event"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions_taken",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="event",
            name="event_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api.eventtype",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="hosts",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="event",
            name="view_groups",
            field=models.ManyToManyField(
                blank=True, related_name="viewable_events", to="auth.group"
            ),
        ),
        migrations.AddConstraint(
            model_name="eventactionrecord",
            constraint=models.UniqueConstraint(
                fields=("acted_on", "event", "action"),
                name="unique_action_per_user_event_pair",
            ),
        ),
    ]
