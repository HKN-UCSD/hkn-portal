from django.core.management.base import BaseCommand
from myapp.api.models.users import Onboarding, Officer

class Command(BaseCommand):
    help = "Create Onboarding objects"

    def handle(self, *args, **kwargs):
        onboarding1 = Onboarding.objects.create_Onboarding(
            quarterInput = "Previous",
            officerInput = False
        )

        onboarding2 = Onboarding.objects.create_Onboarding(
            quarterInput = "Spring 2024",
            officerInput = True
        )

        users = Officer.objects.all()
        for officer in users:
            if (officer.user.induction_class == "Beta Omicron"):
                officer.onboarding = onboarding2
            else:
                officer.onboarding = onboarding1
            officer.save()
