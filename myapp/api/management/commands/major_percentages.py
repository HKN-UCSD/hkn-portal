from django.core.management.base import BaseCommand
from myapp.api.models.users import CustomUser
from collections import Counter

class Command(BaseCommand):
    help = 'Calculate percentage of each major in CustomUser'

    def handle(self, *args, **kwargs):
        users = CustomUser.objects.all()
        total_users = users.count()

        if total_users == 0:
            self.stdout.write("No users found.")
            return

        # Assuming major is a string field. Adjust if it's a ForeignKey.
        majors = [user.major for user in users if user.major]
        users_with_major = [user.major.strip() for user in users if user.major and user.major.strip()]
        users_without_major = total_users - len(users_with_major)

        counts = Counter(majors)

        self.stdout.write("Major Percentages (only among users with a major):\n")
        for major, count in counts.items():
            percentage = (count / len(users_with_major)) * 100
            self.stdout.write(f"{major}: {percentage:.2f}%")

        self.stdout.write(f"\nUsers without major: {users_without_major} ({(users_without_major / total_users) * 100:.2f}%)")
        self.stdout.write(f"Total users: {total_users}")
