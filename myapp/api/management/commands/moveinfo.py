from django.core.management.base import BaseCommand
from myapp.api.models.users import Inductee, Member

class Command(BaseCommand):
    help = "Move fields from inductees and members to base user"

    def handle(self, *args, **kwargs):

        # Get all Inductees
        inductees = Inductee.objects.all()
        for inductee in inductees:
            user = inductee.user
            try:
                user.degree = inductee.degree
                user.grad_year = inductee.grad_year
                user.major = inductee.major
                user.save()
            except:
                print(inductee)
                continue
        
        # Get all Members
        members = Member.objects.all()
        for member in members:
            user = member.user
            try:
                user.degree = member.degree
                user.grad_year = member.grad_year
                user.major = member.major
                user.save()
            except:
                print(member)
                continue
