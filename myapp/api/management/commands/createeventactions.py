from typing import Any
from django.core.management.base import BaseCommand
from myapp.api.models import EventAction
from django.contrib.auth.models import Group
import datetime

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        rsvpaction, _ = EventAction.objects.get_or_create(
            name="rsvp"
        )
        rsvpaction.norole_viewable=True
        rsvpaction.window = EventAction.WindowChoices.B
        rsvpaction.save()

        signinaction, _ = EventAction.objects.get_or_create(
            name="signin"
        )

        signinaction.norole_viewable=True
        signinaction.window = EventAction.WindowChoices.M
        signinaction.start_leeway=datetime.timedelta(minutes=-30)
        signinaction.end_leeway=datetime.timedelta(hours=24)
        signinaction.save()