# Generated by Django 4.2.3 on 2023-10-18 19:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_remove_inductee_preferred_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="hosts",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]