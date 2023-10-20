from django.core.management.base import BaseCommand
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from myapp.api.models.users import InductionClass
from datetime import datetime
import base64

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
            curr_class = ind_class
            break
      if curr_class:
         token = urlsafe_base64_encode(curr_class.name.encode('utf-8'))
         form_link = f"https://portal.hknucsd.com/inductee_form/{token}"
         self.stdout.write(self.style.SUCCESS(f"Inductee form link: {form_link}"))
         print(token)
         print(type(token))
         print(urlsafe_base64_decode(token))
         print(urlsafe_base64_decode(token).decode('utf-8'))
      else:
         self.stdout.write(self.style.ERROR("No current induction class object found.\nUse newinductionclass command to create one."))
