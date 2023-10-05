from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.users import CustomUser
import json

class Command(BaseCommand):
   help = "Generate a json file of inductees"

   def handle(self, *args, **kwargs):
      inductee_group = Group.objects.get(name="inductee")
      inductees = CustomUser.objects.filter(groups=inductee_group)


      user_data = []

      for user in inductees:
         user_data.append({"email": user.email})
      
      output_file = 'inductees.json'

      with open(output_file, 'w') as json_file:
         json.dump(user_data, json_file, indent=4)
      
      print(f"Successfully exported {len(user_data)} inductee(s) to {output_file}")