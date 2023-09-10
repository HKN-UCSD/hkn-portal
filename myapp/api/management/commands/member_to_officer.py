from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from myapp.api.models import CustomUser, Officer
import json


class Command(BaseCommand):
    help = "Upgrade existing members to officers, pass in JSON file as argument. File should include \{email, position\}"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*")

    def handle(self, *args, **kwargs):
        with open(args[0], "r") as f:
            data = json.load(f)

        # data example: [{"email": "example@domain.com", "position": "position"},
        #                {"email": "example2@domain.com", "position": "position 2"}]

        unsuccessful = []
        for entry in data:
            email = entry.get("email")
            position = entry.get("position")

            try:
                user = CustomUser.objects.get(email=email)
                user.groups.add(Group.objects.get(name="officer"))
                officer = Officer(user=user, position=position)
                officer.save()

            except CustomUser.DoesNotExist:
                unsuccessful.append(email)
                continue

        if len(unsuccessful) != 0:
            print(
                f"Succesfully upgraded { len(data) - len(unsuccessful) } out of { len(data) } total members to officers."
            )
            print("\nFailed:")
            for user in unsuccessful:
                print(user)
        else:
            print(
                f"Successfully upgraded { len(data) } out of { len(data) } total members to officers."
            )
