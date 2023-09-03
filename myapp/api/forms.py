# Forms for registering users
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import datetime

class LoginForm(forms.Form):
   email = forms.CharField(max_length=255, label='Email address')
   password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
   class Meta:
      model = CustomUser
      fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
      exclude = ['user_id']
   first_name = forms.CharField(label='First/Preferred name')
   email = forms.EmailField(label='Email address')

class InducteeForm(forms.Form):
   curr_year = datetime.datetime.now().year
   years = [(year, year) for year in range(curr_year, curr_year + 10)]

   first_name = forms.CharField(max_length=65)
   middle_name = forms.CharField(max_length=65, required=False)
   last_name = forms.CharField(max_length=65)
   preferred_name = forms.CharField(max_length=65, required=False)
   major = forms.CharField(max_length=65)
   grad_year = forms.ChoiceField(choices=years, label='Graduation year')


