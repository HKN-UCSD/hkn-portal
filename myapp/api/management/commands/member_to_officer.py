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
                print(
                    f"Upgraded { user.first_name } to officer with position { position }"
                )

            except User.DoesNotExist:
                continue
        if len(unsuccessful) != 0:
            print(
                f"Succesfully upgraded { len(unsuccessful) } out of { len(data) } total members to officers."
            )
            print("Failed:")
            for user in unsuccessful:
                print(user)
