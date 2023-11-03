from django.core.management.base import BaseCommand
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from myapp.api.models.users import InductionClass
from datetime import datetime

"""
This command can be used to create a new link for inductee_form based on induction class
"""
class Command(BaseCommand):
   help = "Create new link for inductee_form"

   def handle(self, *args, **kwargs):
      date = datetime.now().date()
      ind_classes = InductionClass.objects.all()
      curr_class = None
      for ind_class in ind_classes:
         if (date >= ind_class.start_date) and (date < ind_class.end_date):
            if (not curr_class):
               curr_class = ind_class
            # look for induction class with closer start date
            elif ((date - ind_class.start_date) < (date - curr_class.start_date)):
               curr_class = ind_class
      if curr_class:
         curr_class.form_active = True
         curr_class.save()
         token = urlsafe_base64_encode(curr_class.name.encode('utf-8'))
         form_link = f"https://portal.hknucsd.com/inductee_form/{token}/"
         self.stdout.write(self.style.SUCCESS(f"Inductee form link for {curr_class.name}: {form_link}"))
      else:
         self.stdout.write(self.style.ERROR("No current induction class object found.\nUse newinductionclass command to create one."))
