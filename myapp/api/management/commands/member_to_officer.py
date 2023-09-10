from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
import json


class Command(BaseCommand):
    help = "Upgrade existing members to officers"

    def handle(self, *args, **kwargs):
        with open(args[1], "r") as f:
            data = json.load(f)
        # process data:
        # find user based on first name, last name, registered email
        # add user to group 'officer' and create Officer instance
        # assing user to officer.user and position to officer.position
        pass
