from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create user groups"

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name="inductee")
        Group.objects.get_or_create(name="member")
        Group.objects.get_or_create(name="outreach")
        Group.objects.get_or_create(name="officer")
