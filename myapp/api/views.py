from django.http import Http404
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
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from myapp.api.models import Member, Inductee, OutreachStudent, Officer, Admin
from myapp.api.forms import LoginForm, RegisterForm, InducteeForm, OutreachForm



class EventViewSet(ModelViewSet):
    serializer_class = serializers.PublicEventSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # TODO: replace with Django REST object-level permissions
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Event.objects.all()

        user_groups = self.request.user.groups.all()

        if self.request.method == "GET":
            permitted_events_attr = "viewable_events"
        elif self.request.method in ["POST", "PUT", "DELETE"]:
            permitted_events_attr = "editable_events"
        else:
            raise SuspiciousOperation

        viewable_posts = models.Event.objects.all().filter(anon_viewable=True)
        for group in user_groups:
            viewable_posts | getattr(group, permitted_events_attr).all()

        return viewable_posts.distinct()


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


        return Response({"message": "Hello world"})


def log_in(request):
    if request.user.is_authenticated:
        return redirect("spa")

    if request.method == "GET":
        form = LoginForm()
        return render(request, "registration/login.html", {"form": form})

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data["email"], password=form.cleaned_data["password"]
            )
            if user is not None:
                login(request, user)

                # if there is a ?next=
                next_page = request.GET.get("next")
                if next_page:
                    return redirect(next_page)
                return redirect("spa")
            else:
                message = "Your email and password didn't match. Please try again."
        return render(
            request,
            "registration/login.html",
            context={"form": form, "message": message},
        )


def log_out(request):
    logout(request)
    return redirect("login")


def register(request):
    if request.user.is_authenticated:
        return redirect("spa")

    if request.method == "GET":
        form = RegisterForm()
        return render(request, "registration/register.html", {"form": form})

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.first_name = form.cleaned_data["first_name"].title()
            user.last_name = form.cleaned_data["last_name"].title()
            user.save()

            # login user directly
            login(request, user)

            # if there is a ?next=
            next_page = request.GET.get("next")
            if next_page:
                return redirect(next_page)
            return redirect("spa")
        else:
            return render(request, "registration/register.html", {"form": form})


def password_reset(request):
    if request.user.is_authenticated:
        return redirect("spa")

    if request.method == "GET":
        form = PasswordResetForm()
        return render(request, "registration/password_reset.html", {"form": form})

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                email_template_name="registration/password_reset_email.html",
                use_https=request.is_secure(),
            )
            return redirect("password_reset_done")
        else:
            return render(request, "registration/password_reset.html", {"form": form})


def password_reset_done(request):
    if request.user.is_authenticated:
        return redirect("spa")

    return render(request, "registration/password_reset_done.html")


def password_reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_b64decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "GET":
            form = SetPasswordForm(user)
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                success_url = reverse(
                    "password_reset_complete", kwargs={"email": user.get_email()}
                )
                return redirect(success_url)
        return render(
            request, "registration/password_reset_confirm.html", {"form": form}
        )
    else:
        return render(request, "registration/password_reset_invalid.html")


def password_reset_complete(request, email):
    if request.user.is_authenticated:
        return redirect("spa")

    return render(
        request, "registration/password_reset_complete.html", {"email": email}
    )


def inductee_form(request):
    user = request.user
    if request.method == "GET":
        # show completion page if already done
        if user.groups.filter(name="inductee").exists():
            return redirect(reverse("inductee_form_complete"))
        if user.groups.filter(name="member").exists():
            return redirect(reverse("inductee_form_complete"))

        form = InducteeForm()
        return render(request, "registration/inductee_form.html", {"form": form})

    if request.method == "POST":
        form = InducteeForm(request.POST)
        if form.is_valid():
            user.groups.add(Group.objects.get(name="inductee"))
            user.first_name = form.cleaned_data["first_name"].title()
            user.middle_name = form.cleaned_data["middle_name"].title()
            user.last_name = form.cleaned_data["last_name"].title()
            user.save()

            if form.cleaned_data["major"] == "Other":
                inductee_major = form.cleaned_data["other_option"].title()
            else:
                inductee_major = form.cleaned_data["major"]
            inductee = Inductee(
                user=user,
                preferred_name=form.cleaned_data["preferred_name"].title(),
                major=inductee_major,
                degree=form.cleaned_data["degree"],
                grad_year=form.cleaned_data["grad_year"],
            )
            # preferred name = first name if not entered
            if not form.cleaned_data["preferred_name"]:
                inductee.preferred_name = user.first_name
            inductee.save()

            success_url = reverse("inductee_form_complete")
            return redirect(success_url)
        return render(request, "registration/inductee_form.html", {"form": form})


def inductee_form_complete(request):
    user = request.user
    if user.groups.filter(name="inductee").exists():
        return render(request, "registration/form_complete.html")
    if user.groups.filter(name="member").exists():
        return render(request, "registration/form_complete.html")
    else:
        return redirect(reverse("inductee_form"))


def outreach_form(request):
    user = request.user
    if request.method == "GET":
        # show completion page if already done
        if user.groups.filter(name="outreach").exists():
            return redirect(reverse("outreach_form_complete"))

        form = OutreachForm()
        return render(request, "registration/outreach_form.html", {"form": form})

    if request.method == "POST":
        form = OutreachForm(request.POST)
        if form.is_valid():
            user.groups.add(Group.objects.get(name="outreach"))

            outreach_student = OutreachStudent(
                user=user,
                car=form.cleaned_data["car"],
                outreach_course=form.cleaned_data["outreach_course"],
            )
            outreach_student.save()

            success_url = reverse("outreach_form_complete")
            return redirect(success_url)
        return render(request, "registration/outreach_form.html", {"form": form})


def outreach_form_complete(request):
    user = request.user
    if user.groups.filter(name="outreach").exists():
        return render(request, "registration/form_complete.html")
    else:
        return redirect(reverse("outreach_form"))
