from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.events import EventType
from myapp.api.models.users import Major, DegreeLevel

"""
This command initializes user roles and event types

These values should rarely be changed, and therefore should 
not be configurable through the portal, but just through the command line
"""

class Command(BaseCommand):
    help = "Create user groups and event types"

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name="inductee")
        Group.objects.get_or_create(name="member")
        Group.objects.get_or_create(name="outreach")
        Group.objects.get_or_create(name="officer")

        Major.objects.get_or_create(name="BENG: Bioengineering")
        Major.objects.get_or_create(name="BENG: Bioinformatics")
        Major.objects.get_or_create(name="BENG: Biotechnology")
        Major.objects.get_or_create(name="BENG: BioSystems")
        Major.objects.get_or_create(name="CSE: Computer Engineering")
        Major.objects.get_or_create(name="CSE: Computer Science")
        Major.objects.get_or_create(name="CSE: CS-Bioinformaticsg")
        Major.objects.get_or_create(name="DSC: Data Science")
        Major.objects.get_or_create(name="ECE: Computer Engineering")
        Major.objects.get_or_create(name="ECE: Electrical Engineering")
        Major.objects.get_or_create(name="ECE: EE and Society")
        Major.objects.get_or_create(name="ECE: Engineering Physics")
        Major.objects.get_or_create(name="MAE: Aerospace Engineering")
        Major.objects.get_or_create(name="MAE: Environmental Engineering")
        Major.objects.get_or_create(name="MAE: Mechanical Engineering")
        Major.objects.get_or_create(name="MATH: Math-CS")
        Major.objects.get_or_create(name="Other")

        DegreeLevel.objects.get_or_create(name="Undergraduate")
        DegreeLevel.objects.get_or_create(name="Graduate")
        DegreeLevel.objects.get_or_create(name="Doctorate")
        DegreeLevel.objects.get_or_create(name="Other")

        EventType.objects.get_or_create(name="Social")
        EventType.objects.get_or_create(name="Professional")
        EventType.objects.get_or_create(name="Technical")
        EventType.objects.get_or_create(name="Outreach")
        EventType.objects.get_or_create(name="Mentorship")
        EventType.objects.get_or_create(name="General")
