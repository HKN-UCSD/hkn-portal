from django.core.management.base import BaseCommand
from myapp.api.models.users import CustomUser

"""
This command can be used to create a new link for inductee_form based on induction class
"""
class Command(BaseCommand):
    help = "Change default profile path from UserProfile.png to User.png"

    def handle(self, *args, **kwargs):
        users = CustomUser.objects.all()
        for user in users:
            if user.profile_picture == '/static/profile_icons/UserProfile.png':
                user.profile_picture = '/static/profile_icons/User.png'
                user.save()
