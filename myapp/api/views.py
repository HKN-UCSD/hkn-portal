from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer

from django.shortcuts import  render, redirect
from django.contrib.auth import authenticate, login, logout
from myapp.api.forms import LoginForm, RegisterForm

class GreetingApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        return Response({"message": "Hello world"})
    
def log_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('spa')
            else:
                message = 'Your username and password didn\'t match. Please try again.'
        return render(request, 'registration/login.html', context={'form': form, 'message': message})

def log_out(request):
    logout(request)
    return redirect('login')

def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form}) 
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return redirect(f'/accounts/login/?username={user.username}')
        else:
            return render(request, 'registration/register.html', {'form': form})