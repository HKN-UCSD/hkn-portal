from django.core.management.base import BaseCommand
from myapp.api.models.users import Inductee, Member

"""
This command can be used to create a superuser on the hkn portal

We should try to stick to one superuser (hkn.kappa.psi@gmail.com) as only this user
would be allowed to edit the database directly
"""
class Command(BaseCommand):
    help = "Create superuser using the CustomUser model"

    def handle(self, *args, **kwargs):
        inductees = Inductee.objects.all()

        for inductee in inductees:
            user = inductee.user
            try:
                user.major = inductee.major
                user.degree = inductee.degree
                user.grad_year = inductee.grad_year
                user.save()
            except:
                print(inductee)
                continue
        
        members = Member.objects.all()

        for member in members:
            user = member.user
            try:
                user.major = member.major
                user.degree = member.degree
                user.grad_year = member.grad_year
                user.save()
            except:
                print(member)
                continue