from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.events import EventType

"""
This command initializes user roles and event types

These values should rarely be changed, and therefore should 
not be configurable through the portal, but just through the command line
"""

class Command(BaseCommand):
    help = "Create user groups and event types"

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name="inductee")
        Group.objects.get_or_create(name="member")
        Group.objects.get_or_create(name="outreach")
        Group.objects.get_or_create(name="officer")

        EventType.objects.get_or_create(name="Social")
        EventType.objects.get_or_create(name="Professional")
        EventType.objects.get_or_create(name="Technical")
        EventType.objects.get_or_create(name="Outreach")
        EventType.objects.get_or_create(name="Mentorship")
        EventType.objects.get_or_create(name="General")
