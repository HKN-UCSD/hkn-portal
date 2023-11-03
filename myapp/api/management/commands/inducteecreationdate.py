from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.api.models.users import Inductee
from datetime import datetime, time

"""
This command sets all current inductees' creation date to Oct 1, 2023
"""

class Command(BaseCommand):
   help = "Set inductee classes to current class"

   def handle(self, *args, **kwargs):
      inductees = Inductee.objects.all()
      date = datetime.strptime("20231001", "%Y%m%d")
      for inductee in inductees:
         inductee.date_created = timezone.make_aware(datetime.combine(date, time(0,1)))
         inductee.save()