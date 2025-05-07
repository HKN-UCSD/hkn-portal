from django.core.management.base import BaseCommand
from myapp.api.models.users import Quarter
from datetime import datetime

"""
This command can be used to create a new quarter on the hkn portal
"""
class Command(BaseCommand):
   help = "Create Quarter"

   def handle(self, *args, **kwargs):
      date_format = "%Y%m%d"
      name = input("Enter quarter name (eg WI24): ")
      start_date = input("Enter start date (YYYYMMDD) (inclusive): ")
      start_date = datetime.strptime(start_date, date_format).date()

      # Check for overlapping dates
      quarters = Quarter.objects.all()
      for quarter in quarters:
         if (start_date >= quarter.start_date) and (start_date < quarter.end_date):
            self.stdout.write(self.style.ERROR(f"WARNING: Start date is during {quarter.name}'s duration"))
            cont = input("Continue creating induction class? Y/N: ").lower()
            if cont == "y" or cont == "yes":
               break
            else:
               print("Exiting")
               return
            
      end_date = input("Enter end date (YYYYMMDD) (non-inclusive): ")
      end_date = datetime.strptime(end_date, date_format).date()

      academic_year = input("Enter class's academic year (YYYY-YYYY): ")

      if len(academic_year) == 8:
         acad_start = academic_year[:4]
         acad_end = academic_year[4:]
      elif len(academic_year) == 9:
         acad_start = academic_year[:4]
         acad_end = academic_year[5:]
      else:
         self.stdout.writ(self.style.ERROR("Please enter the academic years in the correct format"))
         return

      academic_year = datetime.strptime(acad_start, "%Y").year

      if (end_date < start_date):
         self.stdout.write(self.style.ERROR("Error creating inductee class: end date must be later than start date."))
         return
      try:
         # Create induction class
         quarter = Quarter.objects.create_quarter(
            name = name,
            start_date = start_date,
            end_date = end_date,
            academic_year = academic_year,
         )
         print("\nSuccessfully created new induction class:")
         print("Name: " + quarter.name)
         print("Start date: " + str(quarter.start_date))
         print("End date: " + str(quarter.end_date))
         print("Academic year (only start year is stored): " + str(quarter.academic_year))
         print("Academic year end (for reference): " + str(acad_end))

         quarter.save()
      except Exception as e:
         self.stdout.write(self.style.ERROR(f"Error creating quarter: {e}"))
