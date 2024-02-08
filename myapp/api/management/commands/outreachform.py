from django.core.management.base import BaseCommand
from django.utils.http import urlsafe_base64_encode
from myapp.api.models.users import Quarter
from datetime import datetime

"""
This command can be used to create a new link for outreach_form based on quarter
"""
class Command(BaseCommand):
   help = "Create new link for outreach_form"

   def handle(self, *args, **kwargs):
      date = datetime.now().date()
      quarters = Quarter.objects.all()
      curr_quarter = None
      for quarter in quarters:
         if (date >= quarter.start_date) and (date < quarter.end_date):
            if (not curr_quarter):
               curr_quarter = quarter
            # look for induction class with closer start date
            elif ((date - quarter.start_date) < (date - curr_quarter.start_date)):
               curr_quarter = quarter
      if curr_quarter:
         token = urlsafe_base64_encode(curr_quarter.name.encode('utf-8'))
         form_link = f"https://portal.hknucsd.com/outreach_form/{token}/"
         self.stdout.write(self.style.SUCCESS(f"Outreach form link for {curr_quarter.name}: {form_link}"))
      else:
         self.stdout.write(self.style.ERROR("No current quarter object found.\nUse newquarter command to create one."))
