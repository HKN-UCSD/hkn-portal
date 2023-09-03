# Forms for registering users
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class LoginForm(forms.Form):
   email = forms.CharField(max_length=255)
   password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
   class Meta:
      model = CustomUser
      fields = ['first_name', 'last_name', 'preferred_name', 'email', 'password1', 'password2']
      exclude = ['user_id']
   first_name = forms.CharField(label='First Name*')
