import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.api.models.users import Quarter, Onboarding, Officer, CustomUser

winter_quarter = Quarter.objects.get(name = "WI24")
spring_quarter = Quarter.objects.get(name = "SP24")

# Create onboarding objects, get_or_create returns a tuple. The object vs boolean of it being created or not
previous_onboarding, created_previous = Onboarding.objects.get_or_create(quarter_name="Previous", new_officer=False, quarter_reference = winter_quarter)
spring_onboarding, created_spring = Onboarding.objects.get_or_create(quarter_name="Spring 2024", new_officer=True, quarter_reference = spring_quarter)


# Chehck if objects were created(Only the first time)
if created_previous or created_spring:
    print("First time running?")

# Get all officers and their corresponding custom users
officers = Officer.objects.all().select_related('user')

print(officers)


# Create onboarding instances for each officer
for officer in officers:
    user = officer.user
    # Check if onboarding already exists for this officer and quarter
    if officer and user.induction_class_id == "Beta Omicron":
        
        officer.onboarding_id = spring_onboarding
        officer.save()
        
        print(f"Assigned {user.username} to Spring 2024 Onboarding.")
        
    # Check if officer is not beta omicron but also has something in there i.e not null
    elif officer and (user.induction_class_id != "Beta Omicron" or not user.induction_class):
        
        # Assign to "Previous"
        officer.onboarding_id = previous_onboarding
        officer.save()
        
        print(f"Assigned {user.username} to Previous Onboarding.")

print("Onboarding assignments complete.")
