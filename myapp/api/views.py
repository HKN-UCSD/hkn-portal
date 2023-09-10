from base64 import urlsafe_b64decode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from myapp.api.models import Member, Inductee, OutreachStudent
from myapp.api.forms import LoginForm, RegisterForm, InducteeForm


class GreetingApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        return Response({"message": "Hello world"})


def log_in(request):
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
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "registration/register.html", {"form": form})

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.first_name = form.cleaned_data["first_name"].capitalize()
            user.last_name = form.cleaned_data["last_name"].capitalize()
            user.save()
            user.groups.add(Group.objects.get(name="guest"))

            # login user directly
            # user = authenticate(
            #    email = form.cleaned_data['email'],
            #    password = form.cleaned_data['password1']
            # )
            login(request, user)

            # if there is a ?next=
            next_page = request.GET.get("next")
            if next_page:
                return redirect(next_page)
            return redirect("spa")
        else:
            return render(request, "registration/register.html", {"form": form})


def register_success(request, email):
    return render(request, "registration/register_success.html", {"email": email})


def password_reset(request):
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
    return render(
        request, "registration/password_reset_complete.html", {"email": email}
    )


def inductee_form(request):
    if request.method == "GET":
        # show completion page if already done
        if request.user.groups.filter(name="inductee").exists():
            return redirect(reverse("inductee_form_complete"))

        form = InducteeForm()
        return render(request, "registration/inductee_form.html", {"form": form})

    if request.method == "POST":
        form = InducteeForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data["first_name"].title()
            user.middle_name = form.cleaned_data["middle_name"].capitalize()
            user.last_name = form.cleaned_data["last_name"].capitalize()
            user.save()
            user.groups.remove(Group.objects.get(name="guest"))
            user.groups.add(Group.objects.get(name="inductee"))

            if form.cleaned_data["major"] == "Other":
                inductee_major = form.cleaned_data["other_option"].title()
            else:
                inductee_major = form.cleaned_data["major"]
            inductee = Inductee(
                preferred_name=form.cleaned_data["preferred_name"].capitalize(),
                major=inductee_major,
                degree=form.cleaned_data["degree"],
                grad_year=form.cleaned_data["grad_year"],
            )
            # preferred name = first name if not entered
            if not form.cleaned_data["preferred_name"]:
                inductee.preferred_name = user.first_name
            inductee.user = user
            inductee.save()

            success_url = reverse("inductee_form_complete")
            return redirect(success_url)
        return render(request, "registration/inductee_form.html", {"form": form})


def inductee_form_complete(request):
    user = request.user
    user_id = user.user_id
    context = {"inductee_instance": Inductee.objects.filter(user=user_id).first()}
    return render(request, "registration/inductee_form_complete.html", context)


def outreach_form(request):
    # must be a member to be upgraded to outreach student
    return None
