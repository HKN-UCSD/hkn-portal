# Generated by Django 4.2.3 on 2023-09-01 22:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("api", "0002_remove_eventtype_permitted_groups_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventtype",
            name="view_groups",
            field=models.ManyToManyField(
                blank=True, related_name="viewable_event_types", to="auth.group"
            ),
        ),
    ]
