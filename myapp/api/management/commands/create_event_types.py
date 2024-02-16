from django.core.management.base import BaseCommand
from myapp.api.models.events import EventType


class Command(BaseCommand):
    help = "Create event types"

    def handle(self, *args, **kwargs):
        EventType.objects.get_or_create(name="Social")
        EventType.objects.get_or_create(name="Professional")
        EventType.objects.get_or_create(name="Technical")
        EventType.objects.get_or_create(name="Outreach")
        EventType.objects.get_or_create(name="Mentorship")
        EventType.objects.get_or_create(name="General")
