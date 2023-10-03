from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.users import CustomUser, Inductee, Member
import json


class Command(BaseCommand):
    help = "Promote existing inductees to members, pass in JSON file as argument. File should include \{email\}"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*")

    def handle(self, *args, **kwargs):
        with open(args[0], "r") as f:
            data = json.load(f)

        # data example: [{"email": "example@domain.com"},
        #                {"email": "example2@domain.com"}]

        successful = []
        unsuccessful = []
        for entry in data:
            email = entry.get("email")

            try:
                user = CustomUser.objects.get(email=email)
                inductee = Inductee.objects.filter(user=user.user_id).first()
                if inductee is None:
                    raise Inductee.DoesNotExist(
                        f"No matching Inductee found for user with email { email }"
                    )
                preferred_name = inductee.preferred_name
                major = inductee.major
                degree = inductee.degree
                grad_year = inductee.grad_year
                inductee.delete
                user.groups.remove(Group.objects.get(name="inductee"))

                member = Member(
                    user=user,
                    preferred_name=preferred_name,
                    major=major,
                    degree=degree,
                    grad_year=grad_year,
                )
                member.save()
                user.groups.add(Group.objects.get(name="member"))
                successful.append(f"{ user.first_name } ({email})")

                #For if inductees had setting on_delete = models.CASCADE
                """
                user_id = user.user_id
                first_name = user.first_name
                middle_name = user.middle_name
                last_name = user.last_name
                password = user.password

                inductee = Inductee.objects.filter(user=user_id).first()
                if inductee is None:
                    raise Inductee.DoesNotExist(
                        f"No matching Inductee found for user with email { email }"
                    )
                preferred_name = inductee.preferred_name
                major = inductee.major
                degree = inductee.degree
                grad_year = inductee.grad_year

                user.delete()

                user = CustomUser(
                    user_id=user_id,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
                user.save()

                member = Member(
                    user=user,
                    preferred_name=preferred_name,
                    major=major,
                    degree=degree,
                    grad_year=grad_year,
                )
                member.save()

                user.groups.add(Group.objects.get(name="member"))
                successful.append(f"{ user.first_name } ({email})")
                """

            except CustomUser.DoesNotExist:
                error = (email, "Not a User")
                unsuccessful.append(error)
                continue

            except Inductee.DoesNotExist:
                error = (email, "Not an Inductee")
                unsuccessful.append(error)
                continue

        if len(unsuccessful) != 0:
            if len(successful) != 0:
                print("\nPromoted:")
                for user in successful:
                    print(user)
            print("\nUnsuccessul:")
            for error in unsuccessful:
                print(error)
            print(
                f"\nSuccesfully Promoted { len(successful) } out of { len(data) } total inductees to members."
            )
        else:
            print("\nPromoted:")
            for user in successful:
                print(user)
            print(
                f"\nSuccessfully Promoted { len(data) } out of { len(data) } total inductees to members."
            )
