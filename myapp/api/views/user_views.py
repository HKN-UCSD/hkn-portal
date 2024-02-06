import os
import json
from datetime import datetime, time
from dotenv import load_dotenv
from myapp.settings import BASE_DIR

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from base64 import urlsafe_b64decode

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    action,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from myapp.api.serializers import (
    UserSerializer,
    CustomUserSerializer, 
    InducteeSerializer, 
    MemberSerializer, 
    OutreachStudentSerializer, 
    OfficerSerializer,
    InductionClassSerializer,
    PermissionGroupSerializer,
)
from myapp.api.models.users import (
    Inductee, 
    Member, 
    OutreachStudent, 
    Officer, 
    CustomUser,
    InductionClass,
)
from myapp.api.models.events import (
    Event,
    EventActionRecord,
)
from myapp.api.forms import (
    LoginForm,
    RegisterForm,
    InducteeForm,
    OutreachForm,
)
from myapp.api.permissions import HasAdminPermissions, is_admin
from myapp.api import exceptions as act_exceptions

from django.urls import reverse
from django.http import Http404
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import Group
from django.template.loader import render_to_string

# TODO: Move user-related view code here

load_dotenv(os.path.join(BASE_DIR, '.env'))

#################################################################
## View Sets
#################################################################
class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="self")
    def get_self(self, request):
        serializer = UserSerializer(request.user)
        if serializer.is_valid:
            return Response(serializer.data)
        raise act_exceptions.ForbiddenException
    
    def get_queryset(self):
        if is_admin(self.request.user):
            return CustomUser.objects.all()
        return CustomUser.objects.filter(pk=self.request.user.pk)

class OfficerViewSet(ReadOnlyModelViewSet):
    # Update api fetch request to latest data
    queryset = Officer.objects.all()

    queryset = CustomUser.objects.filter(groups__name='officer')
    serializer_class = CustomUserSerializer
    permission_classes = [HasAdminPermissions]

class InducteeViewSet(ReadOnlyModelViewSet):
    group = Group.objects.get(name='inductee')
    queryset_users = CustomUser.objects.filter(groups = group)
    queryset_inductees = []
    for user in queryset_users:
        queryset_inductees.append(Inductee.objects.filter(user=user.user_id).first())
    
    serializer_class_user = CustomUserSerializer
    serializer_class_inductee = InducteeSerializer
    permission_classes = [HasAdminPermissions]

    
    # django throws a fit if we don't define a queryset, even if we use a
    # custom list. here, we use a custom queryset format composed of tuples of
    # user and inductee objects
    # this is mess lol dont do this
    queryset = []
    for user, inductee in zip(queryset_users, queryset_inductees):
        queryset.append((user,inductee))
    
    # we need to call two serializers here, so we override the list function
    # idea is that we want to combine serialized output of both user
    # (identifying information) and inductee (points)
    # consider using a customer serializer/model instead? consult
    def list(self, request, *args, **kwargs):
        serialized_users = self.serializer_class_user(self.queryset_users, many=True)
        serialized_inductees = self.serializer_class_inductee(self.queryset_inductees, many=True)

        # merge our data
        for idx in range(len(serialized_users.data)):
            serialized_users.data[idx].update(serialized_inductees.data[idx])
        return Response(serialized_users.data, status=status.HTTP_200_OK)

class OutreachViewSet(ReadOnlyModelViewSet):
    group = Group.objects.get(name='outreach')
    queryset_users = CustomUser.objects.filter(groups=group)
    queryset_outreach = []
    for user in queryset_users:
        queryset_outreach.append(OutreachStudent.objects.filter(user=user.user_id).first())
    
    serializer_class_user = CustomUserSerializer
    serializer_class_outreach = OutreachStudentSerializer
    permission_classes = [HasAdminPermissions]

    queryset = []
    for user, outreach in zip(queryset_users, queryset_outreach):
        queryset.append((user,outreach))

    def list(self, request, *args, **kwargs):
        serialized_users = self.serializer_class_user(self.queryset_users, many=True)
        serialized_outreach = self.serializer_class_outreach(self.queryset_outreach, many=True)

        # merge our data
        for idx in range(len(serialized_users.data)):
            serialized_users.data[idx].update(serialized_outreach.data[idx])
        return Response(serialized_users.data, status=status.HTTP_200_OK)


class InductionClassViewSet(ReadOnlyModelViewSet):
    queryset = InductionClass.objects.all()
    serializer_class = InductionClassSerializer
    permission_classes = [HasAdminPermissions]

class UserProfileView(APIView):
    def get(self, request):
        #if request.user.is_authenticated():
            user = request.user
            serializer = CustomUserSerializer(user)
            serializer_data = serializer.data

            if user.groups.filter(name='inductee').exists():
                inductee = Inductee.objects.filter(user=user.user_id).first()
                serializer_data['inductee_data'] = InducteeSerializer(inductee).data

            if user.groups.filter(name='member').exists():
                member = Member.objects.filter(user=user.user_id).first()
                serializer_data['member_data'] = MemberSerializer(member).data

            if user.groups.filter(name='outreach').exists():
                outreach = OutreachStudent.objects.filter(user=user.user_id).first()
                serializer_data['outreach_data'] = OutreachStudentSerializer(outreach).data
            
            if user.groups.filter(name='officer').exists():
                officer = Officer.objects.filter(user=user.user_id).first()
                serializer_data['officer_data'] = OfficerSerializer(officer).data

            return Response(serializer_data, status=status.HTTP_200_OK)

# Note: Making both of these read only so they can't be edited directly from the portal

class GroupsViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = PermissionGroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

#################################################################
## Specific Views for GET Requests
#################################################################


@api_view(["GET"])
def PermissionsView(request):
    return Response(
        {
            "is_admin": is_admin(request.user)
        }
    )

#################################################################
## Authentication Form Methods
#################################################################

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
                email=form.cleaned_data["email"].lower(), password=form.cleaned_data["password"]
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
            user.preferred_name = form.cleaned_data["first_name"].title()
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
            email = form.cleaned_data["email"]
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                user = None

            if user is not None:
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
                context = {
                    'user': user,
                    'protocol': protocol,
                    'domain': domain,
                    'uid': urlsafe_base64_encode(str(user.pk).encode()),
                    'token': default_token_generator.make_token(user),
                }
                email_content = render_to_string('registration/password_reset_email_template.html', context)
                message = Mail(
                    from_email='hkn.kappa.psi@gmail.com',
                    to_emails=email,
                    subject="HKN Portal Password Reset",
                    html_content=email_content,
                )
                try:
                    sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
                    response = sg.send(message)
                except Exception as e:
                    print(str(e))

                return redirect("password_reset_done")
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
                    "password_reset_complete", kwargs={"email": user.email}
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


def inductee_form(request, token):
    MAX_ROLLOVER_POINTS = 3
    # decode induction class name
    try:
        class_name = urlsafe_base64_decode(token).decode('utf-8')
    except:
        return render(
            request, "registration/inductee_form_invalid.html", {"error": "invalid"}
        )

    curr_class = InductionClass.objects.get(name=class_name)

    # check if form is closed
    if not curr_class.form_active:
        return render(
            request, "registration/inductee_form_invalid.html", {"error": "form_closed"}
        )

    date = datetime.now().date()

    if (date >= curr_class.start_date) and (date < curr_class.end_date):
        user = request.user

        if request.method == "GET":
            # show completion page if already member
            if user.groups.filter(name="member").exists():
                return redirect(reverse("inductee_form_complete"))
            
            # show completion page if already an inductee of current cycle
            if user.groups.filter(name="inductee").exists() and user.induction_class == curr_class:
                return redirect(reverse("inductee_form_complete"))

            form = InducteeForm()
            return render(request, "registration/inductee_form.html", {"form": form, "class_token": token})
        
        if request.method == "POST":
            form = InducteeForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name="inductee"))
                user.first_name = form.cleaned_data["first_name"].title()
                user.middle_name = form.cleaned_data["middle_name"].title()
                user.last_name = form.cleaned_data["last_name"].title()
                
                # preferred name = first name if not entered
                if not form.cleaned_data["preferred_name"]:
                    user.preferred_name = user.first_name
                else:
                    user.preferred_name = form.cleaned_data["preferred_name"].title()
                
                user_ind_class = user.induction_class
                user.induction_class = curr_class
                user.save()

                if form.cleaned_data["major"] == "Other":
                    major = form.cleaned_data["other_option"].title()
                else:
                    major = form.cleaned_data["major"]

                user_id = str(user.user_id)

                # create new entry for user in json field
                curr_class.rollover_points[user_id] = {"name":user.first_name + " " + user.last_name}
                
                # existing Inductee object
                try:
                    inductee = Inductee.objects.get(user=user)

                    # update data in case anything changed
                    inductee.major=major
                    inductee.degree=form.cleaned_data["degree"]
                    inductee.grad_year=form.cleaned_data["grad_year"]
                    inductee.save()

                    if user_ind_class != curr_class:
                        rollover_event = Event.objects.get(name=curr_class.rollover_event)

                        # remove all non-inductee points
                        non_inductee = []
                        between_cycles = []
                        for action in EventActionRecord.objects.filter(acted_on=user, action="Check Off"):
                            # anything before becoming inductee
                            if (action.action_time <= inductee.date_created):
                                non_inductee.append((action.event.name, action.points))
                                action.points = 0
                            # anything between last cycle and filling out form for this cycle
                            if ((action.action_time < timezone.make_aware(datetime.now())) and
                                (action.action_time > timezone.make_aware(datetime.combine(user_ind_class.end_date, time(0, 1))))):
                                between_cycles.append((action.event.name, action.points))
                                action.points = 0
                            action.save()
                        curr_class.rollover_points[user_id]["non inductee"] = non_inductee
                        curr_class.rollover_points[user_id]["between cycles"] = between_cycles

                        # roll-over points
                        if user_ind_class != curr_class:
                            rollover_points = min(inductee.total_points, MAX_ROLLOVER_POINTS)
                            sign_in = EventActionRecord.objects.create(
                                action = "Sign In",
                                acted_on = user,
                                event_id = rollover_event.id,
                                user = user,
                            )
                            sign_in.save()

                            # remove all previous points
                            year_rollover = []
                            for action in EventActionRecord.objects.filter(acted_on=user, action="Check Off"):
                                year_rollover.append((action.event.name, action.points))
                                action.points=0
                                action.save()
                            curr_class.rollover_points[user_id]["year rollover"] = year_rollover
                            check_off = EventActionRecord.objects.create(
                                action = "Check Off",
                                acted_on = user,
                                event_id = rollover_event.id,
                                user = user,
                                points = rollover_points,
                            )
                            check_off.save()

                # no Inductee object
                except:
                    # remove all previous points
                    new_inductee = []
                    for action in EventActionRecord.objects.filter(acted_on=user, action="Check Off"):
                        new_inductee.append((action.event.name, action.points))
                        action.points=0
                        action.save()
                    curr_class.rollover_points[user_id]["first time inductee"] = new_inductee

                    inductee = Inductee(
                        user=user,
                        major=major,
                        degree=form.cleaned_data["degree"],
                        grad_year=form.cleaned_data["grad_year"],
                    )
                    inductee.save()

                curr_class.save()
                success_url = reverse("inductee_form_complete")
                return redirect(success_url)
            return render(request, "registration/inductee_form.html", {"form": form})
    else:
        return render(request, "registration/inductee_form_invalid.html")


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
    

###
# RPC, functional style calls
###
def email_view():
    raise Http404