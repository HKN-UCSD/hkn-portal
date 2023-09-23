# Forms for registering users
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
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

    first_name = forms.CharField(label="First/Preferred name")
    email = forms.EmailField(label="Email address")


class InducteeForm(forms.Form):
    curr_year = datetime.datetime.now().year
    years = [(year, year) for year in range(curr_year, curr_year + 10)]
    majors = [
        ("BENG: Bioengineering", "BENG: Bioengineering"),
        ("BENG: Bioinformatics", "BENG: Bioinformatics"),
        ("BENG: Biotechnology", "BENG: Biotechnology"),
        ("BENG: BioSystems", "BENG: BioSystems"),
        ("CSE: Computer Engineering", "CSE: Computer Engineering"),
        ("CSE: Computer Science", "CSE: Computer Science"),
        ("CSE: CS-Bioinformatics", "CSE: CS-Bioinformatics"),
        ("DSC: Data Science", "DSC: Data Science"),
        ("ECE: Computer Engineering", "ECE: Computer Engineering"),
        ("ECE: Electrical Engineering", "ECE: Electrical Engineering"),
        ("ECE: EE and Society", "ECE: EE and Society"),
        ("ECE: Engineering Physics", "ECE: Engineering Physics"),
        ("MAE: Aerospace Engineering", "MAE: Aerospace Engineering"),
        ("MAE: Environmental Engineering", "MAE: Environmental Engineering"),
        ("MAE: Mechanical Engineering", "MAE: Mechanical Engineering"),
        ("MATH: Math-CS", "MATH: Math-CS"),
        ("Other", "Other"),
    ]
    degrees = [
        ("Undergraduate", "Undergraduate"),
        ("Graduate", "Graduate"),
        ("Doctorate", "Doctorate"),
    ]

    first_name = forms.CharField(max_length=65, label="First name*")
    middle_name = forms.CharField(max_length=65, required=False)
    last_name = forms.CharField(max_length=65, label="Last name*")
    preferred_name = forms.CharField(max_length=65, required=False)
    major = forms.ChoiceField(choices=majors)
    other_option = forms.CharField(required=False)
    degree = forms.ChoiceField(choices=degrees)
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
