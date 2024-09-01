import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()

from myapp.api.models.users import Onboarding, Officer, InductionClass, Quarter

previous_onboarding, created = Onboarding.objects.get_or_create(quarter="Previous", new_officer=False) # get_or_create returns a tuple (object, t/f)
spring_2024_onboarding, created = Onboarding.objects.get_or_create(quarter="Spring 2024", new_officer=True)

# Assign Onboarding to officers
# Query officers and their induction class
officers = Officer.objects.all()

for officer in officers:
    # Access induction class from Officer to CustomUser
    induction_class = officer.user.induction_class_id # where is the "_id" from? users.py only have a variable named induction_class
    if induction_class == "Beta Omicron":
        officer.onboarding = spring_2024_onboarding # officer.onboarding assigns to the "onboarding" column
    else:
        officer.onboarding = previous_onboarding
    officer.save()
print("finish :D")