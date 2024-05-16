from django.core.management.base import BaseCommand
from myapp.api.models.users import Officer
from myapp.api.models.users import Onboarding
from myapp.api.models.users import CustomUser
import json ## rn assuming a list of emails of everyone in database is input as json; IDK how to access database just yet
"""
This command can be used to create an Onboarding object
"""
class Command(BaseCommand):
    help = "Assign Onboarding object to users"

    def handle(self, *args, **kwargs):
        with open(args[0], "r") as f:
            data = json.load(f)

        postSP24 = Onboarding()
        postSP24.newOfficer = True
        postSP24.quarter = "Spring 2024"
        preSP24 = Onboarding()
        preSP24.newOfficer = False
        preSP24.quarter = "Previous"

        for entry in data: ## access database directly instead of using data = json.load(f)
            email = entry.get("email")
            user = CustomUser.objects.get(email=email)
            if Officer.objects.get(user=user):
                officer = Officer.objects.get(user=user)
            else:
                continue

            if(officer.user.induction_class == "Beta Omicron"):
                officer.onboarding = postSP24
            else:
                officer.onboarding = preSP24

