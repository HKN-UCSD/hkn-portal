from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.api.models.users import OutreachStudent, Quarter
from datetime import datetime, time

"""
This command sets all current outreach students' quarter to WI24 (current quarter)
"""

class Command(BaseCommand):
    help = "Set outreach students' quarter to current quarter"

    def handle(self, *args, **kwargs):
        curr_quarter = Quarter.objects.filter(name="WI24").first()
        print(curr_quarter)
        outreachStudents = OutreachStudent.objects.all()
        for outreach in outreachStudents:
            print("set " + outreach.user.preferred_name + " to " + curr_quarter.name)
            outreach.quarter = curr_quarter
            outreach.save()