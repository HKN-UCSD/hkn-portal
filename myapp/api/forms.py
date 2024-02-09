# Forms for registering users
from django import forms
from django.contrib.auth.forms import UserCreationForm
from myapp.api.models.users import CustomUser, Majors, DegreeLevel
import datetime

# turn off formatting by 'black'
# fmt: off
class LoginForm(forms.Form):
    email = forms.CharField(max_length=255, label="Email address")
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "password1", "password2"]
        exclude = ["user_id"]

    email = forms.EmailField(label="Email address")


class InducteeForm(forms.Form):
    curr_year = datetime.datetime.now().year
    years = [(year, year) for year in range(curr_year, curr_year + 10)]
    database_majors = Majors.objects.all()
    majors = [(major.name, major.name) for major in database_majors]
    
    database_degree_levels = DegreeLevel.objects.all()
    degree_levels = [(degree.name, degree.name) for degree in database_degree_levels]

    first_name = forms.CharField(max_length=65, label="(Legal) First name*")
    middle_name = forms.CharField(max_length=65, required=False)
    last_name = forms.CharField(max_length=65, label="Last name*")
    preferred_name = forms.CharField(max_length=65, required=False)
    major = forms.ChoiceField(choices=majors)
    other_major = forms.CharField(required=False)
    degree = forms.ChoiceField(choices=degree_levels)
    other_degree = forms.CharField(required=False)
    grad_year = forms.ChoiceField(choices=years, label="Graduation year")


class OutreachForm(forms.Form):
    car_choices = [
        ("Yes", "Yes"),
        ("No", "No"),
    ]
    courses = [
        ("CSE", "CSE 198"),
        ("ECE", "ECE 198"),
        ("MAE", "MAE 198"),
    ]
    car = forms.ChoiceField(choices=car_choices, label="Do you have a car",
                            widget=forms.RadioSelect(attrs={'style': 'display: inline-block'}))
    outreach_course = forms.ChoiceField(choices=courses)
