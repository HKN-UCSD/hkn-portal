from django.core.management.base import BaseCommand
from myapp.api.models.events import EventActionRecord
from myapp.api.models.users import CustomUser
import json

class Command(BaseCommand):
    help = "Clear all outreach points of given users"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*")

    def handle(self, *args, **kwargs):
        with open(args[0], "r") as f:
            data = json.load(f)
        
        strFormat = "Removed {hours} hours from {user}"
        result = []

        for entry in data:
            email = entry.get("email")
            user = CustomUser.objects.get(email=email)

            actionRecords = EventActionRecord.objects.filter(event__event_type = "Outreach", acted_on=user, action = "Check Off")
            userHours = 0
            for record in actionRecords:
                if record.points != 0:
                    userHours += record.points
                    record.points = 0
                    record.save()

            result.append(strFormat.format(hours = userHours, user = user))
        for entry in result:
            print(entry)