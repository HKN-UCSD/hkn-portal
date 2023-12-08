from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from myapp.api.models.users import CustomUser, Inductee, Member, InductionClass
from datetime import datetime
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
                if Member.objects.filter(user=user.user_id).first() is not None:
                    inductee = None
                else:
                    inductee = Inductee.objects.filter(user=user.user_id).first()
                if inductee is None:
                    raise Inductee.DoesNotExist(
                        f"No matching Inductee found for user with email { email }"
                    )
                major = inductee.major
                degree = inductee.degree
                grad_year = inductee.grad_year
                inductee.delete
                user.groups.remove(Group.objects.get(name="inductee"))

                today = datetime.now().date()
                ind_classes = InductionClass.objects.all()
                induction_class = None
                for ind_class in ind_classes:
                    if ((today >= ind_class.start_date) and (today < ind_class.end_date)):
                        induction_class = ind_class

                if induction_class == None:
                    print("No matching induction class found, all inducted members have class 'None'")

                member = Member(
                    user=user,
                    major=major,
                    degree=degree,
                    grad_year=grad_year,
                )
                member.save()
                user.groups.add(Group.objects.get(name="member"))
                user.induction_class = induction_class
                user.save()
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
            print("\nUnsuccessful:")
            for error in unsuccessful:
                print(error)
            print(
                f"\nSuccessfully Promoted { len(successful) } out of { len(data) } total inductees to members."
            )
        else:
            print("\nPromoted:")
            for user in successful:
                print(user)
            print(
                f"\nSuccessfully Promoted { len(data) } out of { len(data) } total inductees to members."
            )
