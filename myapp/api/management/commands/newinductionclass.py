from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.api.models.users import InductionClass
from myapp.api.models.events import Event, EventType
from datetime import datetime, timedelta

"""
This command can be used to create a new induction class on the hkn portal
"""
class Command(BaseCommand):
   help = "Create InductionClass"

   def handle(self, *args, **kwargs):
      date_format = "%Y%m%d"
      name = input("Enter induction class name: ")
      start_date = input("Enter start date (YYYYMMDD) (inclusive): ")
      start_date = datetime.strptime(start_date, date_format).date()

      # Check for overlapping dates
      ind_classes = InductionClass.objects.all()
      for ind_class in ind_classes:
         if (start_date >= ind_class.start_date) and (start_date < ind_class.end_date):
            self.stdout.write(self.style.ERROR(f"WARNING: Start date is during {ind_class.name}'s induction duration"))
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
         induction_class = InductionClass.objects.create_induction_class(
            name = name,
            start_date = start_date,
            end_date = end_date,
            academic_year = academic_year,
         )
         print("\nSuccessfully created new induction class:")
         print("Name: " + induction_class.name)
         print("Start date: " + str(induction_class.start_date))
         print("End date: " + str(induction_class.end_date))
         print("Academic year (only start year is stored): " + str(induction_class.academic_year))
         print("Academic year end (for reference): " + str(acad_end))

         # Create event to use for point rollover
         # Today 12am
         start_time = timezone.make_aware(datetime.combine(start_date, datetime.min.time()) + timedelta(minutes=1))
         event = Event(
            name = f"{name} Rollover",
            description = f"Points rollover for {name} induction class across academic year",
            is_draft = False,
            start_time = start_time,
            end_time = start_time + timedelta(minutes=14),
            event_type = EventType.objects.get(name="General"),
         )
         event.save()
         induction_class.rollover_event = event.name
         induction_class.save()
      except Exception as e:
         self.stdout.write(self.style.ERROR(f"Error creating inductee class: {e}"))
