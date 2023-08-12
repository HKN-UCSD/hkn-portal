from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer

from django.shortcuts import  render, redirect
from myapp.api.forms import RegisterForm

class GreetingApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        return Response({"message": "Hello world"})
    
def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'registration/register.html', { 'form': form}) 
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return redirect(f'/accounts/login/?username={user.username}')
        else:
            return render(request, 'registration/register.html', {'form': form})