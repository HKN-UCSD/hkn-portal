from django.core.management.base import BaseCommand
from myapp.api.models.users import InductionClass
from datetime import datetime

"""
This command can be used to create a superuser on the hkn portal

We should try to stick to one superuser (hkn.kappa.psi@gmail.com) as only this user
would be allowed to edit the database directly
"""
class Command(BaseCommand):
   help = "Create InducteeClass"

   def handle(self, *args, **kwargs):
      name = input("Enter induction class name: ")
      start_date = input("Enter start date (YYYYMMDD) (inclusive): ")
      end_date = input("Enter end date (YYYYMMDD) (non-inclusive): ")

      date_format = "%Y%m%d"
      start_date = datetime.strptime(start_date, date_format)
      end_date = datetime.strptime(end_date, date_format)
      if (end_date < start_date):
         self.stdout.write(self.style.ERROR("Error creating inductee class: end date must be later than start date."))
         return
      try:
         induction_class = InductionClass.objects.create_induction_class(
            name = name,
            start_date = start_date,
            end_date = end_date,
         )
      except Exception as e:
         self.stdout.write(self.style.ERROR(f"Error creating inductee class: {e}"))
