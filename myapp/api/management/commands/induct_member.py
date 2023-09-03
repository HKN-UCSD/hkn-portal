from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

# Should look through each inductee and verify if they have satisfied induction requirements
# 
class Command(BaseCommand):
    help = 'Reassign user from inductee to member'

    def handle(self, *args, **kwargs):
        user.groups.filter(name='inductee').exists()