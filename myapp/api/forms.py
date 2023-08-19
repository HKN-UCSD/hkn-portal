# Forms for registering users
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class LoginForm(forms.Form):
   username = forms.CharField(max_length=65)
   password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
   class Meta:
      model = CustomUser
      fields = ['username', 'email', 'password1', 'password2']
      exclude = ['user_id']