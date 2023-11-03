from django.core.management.base import BaseCommand
from myapp.api.models.users import Inductee, InductionClass
from datetime import datetime

"""
This command sets all current inductees' induction class to the current class
"""

class Command(BaseCommand):
   help = "Set inductee classes to current class"

   def handle(self, *args, **kwargs):
      count = 0
      inductees = Inductee.objects.all()
      ind_classes = InductionClass.objects.all()
      date = datetime.now().date()
      curr_class = None
      for ind_class in ind_classes:
         if (date >= ind_class.start_date) and (date < ind_class.end_date):
            curr_class = ind_class
            break
      if curr_class:
         for inductee in inductees:
            user = inductee.user
            if user:
               if user.groups.filter(name="inductee").exists():
                  user.induction_class = curr_class
                  user.save()
                  count += 1
      print(f"{count} inductee classes changed")