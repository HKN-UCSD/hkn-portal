from django.core.management.base import BaseCommand
from myapp.api.models.users import Onboarding, Officer

class Command(BaseCommand):
    help = "Create Onboarding entries and assign them to officers"

    def handle(self, *args, **options):
        prev, _ = Onboarding.objects.get_or_create(quarter="Previous", newOfficer=False)
        spring, _ = Onboarding.objects.get_or_create(quarter="Spring 2025", newOfficer=True)

        
        for off in Officer.objects.all():
            if off.induction_class_id == "Beta Rho":
                off.onboarding = spring
            else:
                off.onboarding = prev
            off.save()
        