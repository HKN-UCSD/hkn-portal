# Generated by Django 4.2.3 on 2023-09-01 21:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="eventtype",
            name="permitted_groups",
        ),
        migrations.AddField(
            model_name="eventtype",
            name="edit_groups",
            field=models.ManyToManyField(
                related_name="editable_event_types", to="auth.group"
            ),
        ),
        migrations.AddField(
            model_name="eventtype",
            name="view_groups",
            field=models.ManyToManyField(
                related_name="viewable_event_types", to="auth.group"
            ),
        ),
    ]
