from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.users import CustomUser, Inductee, Member
import json

class Command(BaseCommand):
   help = "Populate preferred name for all users"

   def handle(self, *args, **kwargs):
      for user in CustomUser.objects.all():
         if (user.preferred_name == ""):
            user.preferred_name = user.first_name
         user.save()