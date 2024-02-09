from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.events import EventType
from myapp.api.models.users import Majors, DegreeLevel

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

        Majors.objects.get_or_create(name="BENG: Bioengineering")
        Majors.objects.get_or_create(name="BENG: Bioinformatics")
        Majors.objects.get_or_create(name="BENG: Biotechnology")
        Majors.objects.get_or_create(name="BENG: BioSystems")
        Majors.objects.get_or_create(name="CSE: Computer Engineering")
        Majors.objects.get_or_create(name="CSE: Computer Science")
        Majors.objects.get_or_create(name="CSE: CS-Bioinformaticsg")
        Majors.objects.get_or_create(name="DSC: Data Science")
        Majors.objects.get_or_create(name="ECE: Computer Engineering")
        Majors.objects.get_or_create(name="ECE: Electrical Engineering")
        Majors.objects.get_or_create(name="ECE: EE and Society")
        Majors.objects.get_or_create(name="ECE: Engineering Physics")
        Majors.objects.get_or_create(name="MAE: Aerospace Engineering")
        Majors.objects.get_or_create(name="MAE: Environmental Engineering")
        Majors.objects.get_or_create(name="MAE: Mechanical Engineering")
        Majors.objects.get_or_create(name="MATH: Math-CS")
        Majors.objects.get_or_create(name="Other")

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
