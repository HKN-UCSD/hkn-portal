from django.core.management.base import BaseCommand
from api.models import CustomUser
import uuid


class Command(BaseCommand):
    help = "Create superuser using the CustomUser model"

    def handle(self, *args, **kwargs):
        email = input("Enter email: ")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        password = input("Enter password: ")

        try:
            user = CustomUser.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating superuser: {e}"))
