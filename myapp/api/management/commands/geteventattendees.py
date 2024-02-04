from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.users import CustomUser
from myapp.api.models.events import EventActionRecord
import json

class Command(BaseCommand):
    help = "Generate a json file of inductees"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*")

    def handle(self, *args, **kwargs):
        RSVPactionrecords = EventActionRecord.objects.filter(action="RSVP", event=args[0])
        for record in RSVPactionrecords:
            print(record.acted_on.email)
      
        # output_file = 'inductees.json'

        # with open(output_file, 'w') as json_file:
        #     json.dump(user_data, json_file, indent=4)
        
        # print(f"Successfully exported {len(user_data)} inductee(s) to {output_file}")