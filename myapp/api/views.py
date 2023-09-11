from rest_framework import status
from base64 import urlsafe_b64decode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import connection
from django.core.exceptions import SuspiciousOperation
from django.db.models import Q
from . import models, serializers


class EventViewSet(ModelViewSet):
    serializer_class = serializers.PublicEventSerializer

    # TODO: replace with Django REST permissions
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Event.objects.all()

        user_groups = self.request.user.groups.all()
        all_event_types = models.EventType.objects.all()

        if self.request.method == "GET":
            permitted_event_types = [
                event_type
                for event_type in all_event_types
                if event_type.view_groups.intersection(user_groups)
            ]
        elif self.request.method in ["POST", "PUT", "DELETE"]:
            permitted_event_types = [
                event_type
                for event_type in all_event_types
                if event_type.edit_groups.intersection(user_groups)
            ]
        else:
            raise SuspiciousOperation

        permitted_events = models.Event.objects.all().filter(
            event_type__in=permitted_event_types
        )
        return permitted_events

from django.urls import reverse
from django.shortcuts import  render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from myapp.api.forms import LoginForm, RegisterForm

class EventTypeViewSet(ModelViewSet):
    queryset = models.EventType.objects.all()
    serializer_class = serializers.EventTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RootApi(APIView):
    def get(self, request, format=None):
        return Response(
            {
                "eventlist": reverse("eventlist", request=request, format=format),
                "eventinstance": reverse(
                    "eventinstance", request=request, format=format, kwargs={"pk": 0}
                ),
            }
        )

    
def log_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email = form.cleaned_data['email'],
                password = form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('spa')
            else:
                message = 'Your email and password didn\'t match. Please try again.'
        return render(request, 'registration/login.html', context={'form': form, 'message': message})

def log_out(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form}) 
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            success_url = reverse('register_success', kwargs={'email': user.email})
            return redirect(success_url)
        else:
            return render(request, 'registration/register.html', {'form': form})

def register_success(request, email):
    return render(request, 'registration/register_success.html', {'email': email})

def password_reset(request):
    if request.method == 'GET':
        form = PasswordResetForm()
        return render(request, 'registration/password_reset.html', {'form': form})
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request = request,
                email_template_name = 'registration/password_reset_email.html',
                use_https = request.is_secure(),
            )
            return redirect('password_reset_done')
        else:
            return render(request, 'registration/password_reset.html', {'form': form})

def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_b64decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'GET':
            form = SetPasswordForm(user)
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                success_url = reverse('password_reset_complete', kwargs={'email': user.get_username()})
                return redirect(success_url)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'registration/password_reset_invalid.html')

def password_reset_complete(request, email):
    return render(request, 'registration/password_reset_complete.html', {'email': email})