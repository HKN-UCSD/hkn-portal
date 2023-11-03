from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.users import CustomUser, Officer
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

        successful = []
        unsuccessful = []
        updated = []
        unchanged = []
        for entry in data:
            email = entry.get("email")
            position = entry.get("position")

            try:
                user = CustomUser.objects.get(email=email)
                if user.groups.filter(name="officer").exists():
                    officer = Officer.objects.filter(user=user.user_id).first()
                    if officer.position != position:
                        officer.position = position
                        officer.save()
                        updated.append(
                            f"Updated { user.first_name }'s position to { position }"
                        )
                    else:
                        unchanged.append(f"{ user.first_name } did not change")
                else:
                    user.groups.add(Group.objects.get(name="officer"))
                    officer = Officer(user=user, position=position)
                    officer.save()
                    successful.append(
                        f"{ user.first_name } ({ email }): { officer.position }"
                    )

            except CustomUser.DoesNotExist:
                unsuccessful.append(email)
                continue

        if len(successful) != 0:
            print("\nPromoted:")
            for message in successful:
                print(message)
        if len(updated) != 0:
            print("\nUpdated:")
            for message in updated:
                print(message)
        if len(unchanged) != 0:
            print("\nUnchanged:")
            for message in unchanged:
                print(message)
        if len(unsuccessful) != 0:
            print("\nUnsuccessful:")
            for email in unsuccessful:
                print(email)
        print(
            f"\nSuccessfully promoted { len(successful) } out of { len(data) } total users to officers."
        )