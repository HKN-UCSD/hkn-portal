import os
import json
from datetime import datetime, time
from dotenv import load_dotenv
from myapp.settings import BASE_DIR

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control


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
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from myapp.api.serializers import (
    UserSerializer,
    CustomUserSerializer,
    InducteeSerializer,
    MemberSerializer,
    OutreachStudentSerializer,
    OfficerSerializer,
    InductionClassSerializer,
    PermissionGroupSerializer,
    MajorSerializer,
    DegreeLevelSerializer,
)
from myapp.api.models.users import (
    Inductee,
    Member,
    OutreachStudent,
    Officer,
    CustomUser,
    InductionClass,
    Quarter,
    Major,
    DegreeLevel
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
from myapp.api.permissions import HasAdminPermissions, is_admin, HasMemberPermissions, is_member
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
class MajorViewSet(ReadOnlyModelViewSet):
    serializer_class = MajorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Major.objects.all()


class DegreeLevelViewSet(ReadOnlyModelViewSet):
    serializer_class = DegreeLevelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return DegreeLevel.objects.all()


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
        payload = CustomUser.objects.all()
        eventid = self.request.GET.get("eventid")

        # allow for eventid getparameter: get all users who have attended the event
        # identified by eventid
        # TODO: See if this can be optimized; perhaps a single ORM expression
        # could capture all the users in an event.
        if (eventid is not None):
            all_actions = Event.objects.get(pk=eventid).eventactionrecord_set.all()
            user_set = set()
            for action in all_actions:
                user_set.add(action.user.pk)
            payload = payload.filter(pk__in=user_set)
        if is_admin(self.request.user):
            return payload
        return payload.filter(pk=self.request.user.pk)

class MemberViewSet(ReadOnlyModelViewSet):
    serializer_class_user = CustomUserSerializer
    serializer_class_member = MemberSerializer
    permission_classes = [HasMemberPermissions]

    # Filter members by group
    def get_queryset(self):
        group = Group.objects.get(name='member')
        queryset_users = CustomUser.objects.filter(groups=group)
        queryset_members = [
            Member.objects.filter(user=user.user_id).first()
            for user in queryset_users
        ]
        return list(zip(queryset_users, queryset_members))

    @method_decorator(cache_control(public=True, max_age= 60 * 10))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset:
            serialized_users = self.serializer_class_user([user for user, member in queryset], many=True)
            serialized_member = self.serializer_class_member([member for user, member in queryset], many=True)

            # merge our data
            for idx in range(len(serialized_users.data)):
                serialized_users.data[idx].update(serialized_member.data[idx])
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)
        
class OfficerViewSet(ReadOnlyModelViewSet):
    serializer_class_user = CustomUserSerializer
    serializer_class_officer = OfficerSerializer
    permission_classes = [HasAdminPermissions]

    def get_queryset(self):
        group = Group.objects.get(name='officer')
        queryset_users = CustomUser.objects.filter(groups = group)
        queryset_officers = [
            Officer.objects.filter(user = user.user_id).first()
            for user in queryset_users
        ]
        return list(zip(queryset_users, queryset_officers))

    # we need to call two serializers here, so we override the list function
    # idea is that we want to combine serialized output of both user
    # (identifying information) and inductee (points)
    # consider using a customer serializer/model instead? consult
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset:
            serialized_users = self.serializer_class_user([user for user, officer in queryset], many=True)
            serialized_officer = self.serializer_class_officer([officer for user, officer in queryset], many=True)

            # merge our data
            for idx in range(len(serialized_users.data)):
                serialized_users.data[idx].update(serialized_officer.data[idx])
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)
        
class InducteeViewSet(ReadOnlyModelViewSet):
    serializer_class_user = CustomUserSerializer
    serializer_class_inductee = InducteeSerializer
    permission_classes = [HasAdminPermissions]

    def get_queryset(self):
        group = Group.objects.get(name='inductee')
        queryset_users = CustomUser.objects.filter(groups = group)
        queryset_inductees = [
            Inductee.objects.filter(user=user.user_id).first()
            for user in queryset_users
        ]
        return list(zip(queryset_users, queryset_inductees))

    @method_decorator(cache_control(public=True, max_age= 60 * 10))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset:
            serialized_users = self.serializer_class_user([user for user, inductee in queryset], many=True)
            serialized_inductee = self.serializer_class_inductee([inductee for user, inductee in queryset], many=True)

            # merge our data
            for idx in range(len(serialized_users.data)):
                serialized_users.data[idx].update(serialized_inductee.data[idx])
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)

class OutreachViewSet(ReadOnlyModelViewSet):
    serializer_class_user = CustomUserSerializer
    serializer_class_outreach = OutreachStudentSerializer
    permission_classes = [HasAdminPermissions]

    def get_queryset(self):
        group = Group.objects.get(name='outreach')
        queryset_users = CustomUser.objects.filter(groups=group)
        queryset_outreach = [
            OutreachStudent.objects.filter(user=user.user_id).first()
            for user in queryset_users
        ]
        return list(zip(queryset_users, queryset_outreach))

    @method_decorator(cache_control(public=True, max_age= 60 * 10))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset:
            serialized_users = self.serializer_class_user([user for user, outreach in queryset], many=True)
            serialized_outreach = self.serializer_class_outreach([outreach for user, outreach in queryset], many=True)

            # merge our data
            for idx in range(len(serialized_users.data)):
                serialized_users.data[idx].update(serialized_outreach.data[idx])
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


class InductionClassViewSet(ModelViewSet):
    queryset = InductionClass.objects.all()
    serializer_class = InductionClassSerializer
    permission_classes = [IsAuthenticated]

    def get_curr_induction_class(self):
        """
        Select the induction class with earliest start date with an end date later than today
        """
        induction_classes = InductionClass.objects.all()
        curr_induction_class = induction_classes.filter(
            start_date__lte=datetime.now().date(),
            end_date__gte=datetime.now().date()
        ).first()

        if (curr_induction_class == None):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return curr_induction_class


    # Update availability at the class level
    @action(detail=False, methods=['POST'], url_path='set_availability')
    def update_availability(self, request, pk=None):
        """
        Update availability for a user at the class level.
        """
        # Find current induction class
        curr_induction_class = self.get_curr_induction_class()

        # Retrieve availability array from database
        user_id = request.user.user_id
        availability = request.data.get("availability")

        # Check availability format
        if not availability or len(availability) != 7 or not all(len(day) == 48 for day in availability):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        curr_induction_class.availabilities.update({str(user_id): availability})
        curr_induction_class.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='all_availabilities')
    def list_all_availabilities(self, request, pk=None):
        """
        Retrieve all availabilities for a specific induction class.
        """
        # Find current induction class
        curr_induction_class = self.get_curr_induction_class()

        # Retrieve all availabilities (inductees and officers)
        overall_availability = [[{'inductees': [], 'officers': []} for _ in range(48)] for _ in range(7)]
        for (user_id, availability) in curr_induction_class.availabilities.items():
            user = CustomUser.objects.get(user_id=user_id)
            name = user.preferred_name + " " + user.last_name
            user_type = 'inductee' if user.groups.filter(name='inductee').exists() else 'officer'
            for i in range(7):
                for j in range(48):
                    if availability[i][j] == 1:
                        if (user_type == 'inductee'):
                            overall_availability[i][j]['inductees'].append(name)
                        elif (user_type == 'officer'):
                            overall_availability[i][j]['officers'].append(name)
        return Response(overall_availability, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='inductee_availabilities')
    def get_inductee_availabilities(self, request, pk=None):
        '''
        Retrieve all inductees who filled out availabilities for a specific induction class.
        '''
        # Find current induction class
        curr_induction_class = self.get_curr_induction_class()

        # Retrieve inductee availabilities
        inductees = {}
        for (user_id, availability) in curr_induction_class.availabilities.items():
            user = CustomUser.objects.get(user_id=user_id)
            if user.groups.filter(name='inductee').exists():
                inductees[user_id] =  [f'{user.preferred_name} {user.last_name}', availability]

        return Response(inductees, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='get_availability')
    def individual_availability(self, request, pk=None):
        """
        Query through the induction class field and retrieve the availability of the select user
        Retrieve individual availability for a specific induction class.
        """
        user_id = request.user.user_id

        # Find current induction class
        curr_induction_class = self.get_curr_induction_class()

        # Return the availability of the user
        empty = [[0 for _ in range(48)] for _ in range(7)]
        return Response(curr_induction_class.availabilities.get(str(user_id), empty), status=status.HTTP_200_OK)

class UserProfileViewSet(ModelViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self, user):
        queryset = CustomUser.objects.filter(user_id = user.user_id)
        return queryset

    def get_data(self, user):
        serializer = CustomUserSerializer(user)
        serializer_data = serializer.data

        if user.groups.filter(name='inductee').exists():
            inductee = Inductee.objects.filter(user=user.user_id).first()
            serializer_data['Inductee'] = InducteeSerializer(inductee).data
            serializer_data['induction_class'] = InductionClassSerializer(user.induction_class).data

        if user.groups.filter(name='member').exists():
            member = Member.objects.filter(user=user.user_id).first()
            serializer_data['Member'] = MemberSerializer(member).data
            if (user.induction_class):
                serializer_data['induction_class'] = InductionClassSerializer(user.induction_class).data

        if user.groups.filter(name='outreach').exists():
            outreach = OutreachStudent.objects.filter(user=user.user_id).first()
            serializer_data['Outreach Student'] = OutreachStudentSerializer(outreach).data

        if user.groups.filter(name='officer').exists():
            officer = Officer.objects.filter(user=user.user_id).first()
            serializer_data['Officer'] = OfficerSerializer(officer).data

        return Response(serializer_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="(?P<user_id>[^/.]+)") # Regex needed to read user_id
    def get_profile(self, request, user_id):
        try:
            user = get_object_or_404(CustomUser, user_id = user_id)
        except:
            user = request.user
        return self.get_data(user)

    @action(detail=False, methods=["POST"], url_path="edit")
    def edit_profile(self, request):
        user = request.user
        data = request.data
        user.preferred_name = data.get("preferred_name")
        user.major = data.get("major")
        user.bio = data.get("bio")
        user.grad_year = data.get("grad_year")
        user.social_links = data.get("social_links")
        user.current_courses = data.get("current_courses", [])
        user.save()

        if user.groups.filter(name='inductee').exists():
            inductee = Inductee.objects.filter(user=user.user_id).first()
            inductee.major = data.get("major")
            inductee.degree = data.get("degree")
            inductee.grad_year = data.get("grad_year")
            inductee.save()
        if user.groups.filter(name='member').exists():
            member = Member.objects.filter(user=user.user_id).first()
            member.major = data.get("major")
            member.degree = data.get("degree")
            member.grad_year = data.get("grad_year")
            member.current_courses = data.get("current_courses", [])
            member.save()
        if user.groups.filter(name='outreach').exists():
            outreach = OutreachStudent.objects.filter(user=user.user_id).first()
            outreach.car = data.get("car")
            outreach.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="editIcon")
    def edit_icon(self, request):
        user = request.user
        data = request.data
        user.profile_picture = data.get("profile_picture")
        user.save()
        return Response(status=status.HTTP_200_OK)

# Note: Making both of these read only so they can't be edited directly from the portal

class GroupsViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = PermissionGroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class LeaderBoardViewSet(ReadOnlyModelViewSet):
    """
    ViewSet to return top 10 users and current user's rank
    """
    def list(self, request):
        # Get all members and officers
        members = list(Member.objects.all())
        officers = list(Officer.objects.all())

        # Create a dictionary to track unique users, prioritizing Officer role
        unique_users = {}
        
        # Add officers first
        for officer in officers:
            user_id = str(officer.user.user_id)
            unique_users[user_id] = {
                "preferred_name": officer.user.preferred_name,
                "last_name": officer.user.last_name,
                "role": "Officer",
                "total_points": officer.total_points,
                "user_id": user_id,
            }
        
        # Add members only if they're not already added as officers
        for member in members:
            user_id = str(member.user.user_id)
            if user_id not in unique_users:
                unique_users[user_id] = {
                    "preferred_name": member.user.preferred_name,
                    "last_name": member.user.last_name,
                    "role": "Member",
                    "total_points": member.total_points,
                    "user_id": user_id,
                }

        # Sort all users by total points
        all_sorted_users = sorted(
            unique_users.values(),
            key=lambda x: x["total_points"],
            reverse=True
        )

        # Find current user's rank
        current_user_id = str(request.user.user_id)
        current_user_rank = None
        for index, user in enumerate(all_sorted_users):
            if user["user_id"] == current_user_id:
                current_user_rank = {
                    **user,
                    "rank": index + 1,
                    "total_points": user["total_points"]
                }
                break

        return Response({
            "top_users": all_sorted_users[:10],
            "current_user": current_user_rank
        }, status=status.HTTP_200_OK)

#################################################################
## Specific Views for GET Requests
#################################################################
@api_view(["GET"])
def PermissionsView(request):
    return Response(
        {
            "is_admin": is_admin(request.user),
            "is_member": is_member(request.user)
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

        # Access form
        if request.method == "GET":
            # show completion page if already member
            if user.groups.filter(name="member").exists():
                return redirect(reverse("inductee_form_complete"))

            # show completion page if already an inductee of current cycle
            if user.groups.filter(name="inductee").exists() and user.induction_class == curr_class:
                return redirect(reverse("inductee_form_complete"))

            form = InducteeForm()
            return render(request, "registration/inductee_form.html", {"form": form, "class_token": token})

        # Submit form
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
                    major = form.cleaned_data["other_major"].title()
                else:
                    major = form.cleaned_data["major"]

                if form.cleaned_data["degree"] == "Other":
                    degree = form.cleaned_data["other_degree"].title()
                else:
                    degree = form.cleaned_data["degree"]

                user_id = str(user.user_id)

                # create new entry for user in json field
                curr_class.rollover_points[user_id] = {"name":user.first_name + " " + user.last_name}

                # existing Inductee object
                try:
                    inductee = Inductee.objects.get(user=user)

                    # update data in case anything changed
                    inductee.major=major
                    inductee.degree=degree
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
                                event_id = rollover_event.pk,
                                user = user,
                            )
                            sign_in.save()

                            # remove all previous points
                            rollover = []
                            for action in EventActionRecord.objects.filter(acted_on=user, action="Check Off"):
                                rollover.append((action.event.name, action.points))
                                action.points=0
                                action.save()
                            curr_class.rollover_points[user_id]["rollover"] = rollover
                            check_off = EventActionRecord.objects.create(
                                action = "Check Off",
                                acted_on = user,
                                event_id = rollover_event.pk,
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
                        degree=degree,
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


def outreach_form(request, token):
    # decode quarter name
    try:
        quarter_name = urlsafe_base64_decode(token).decode('utf-8')
    except:
        return render(
            request, "registration/outreach_form_invalid.html", {"error": "invalid"}
        )

    curr_quarter = Quarter.objects.get(name=quarter_name)

    user = request.user

    if request.method == "GET":
        # show completion page if form already completed for current quarter
        try:
            outreach_student = OutreachStudent.objects.filter(user=user.user_id).first()
            if  outreach_student and outreach_student.quarter == curr_quarter:
                return redirect(reverse("outreach_form_complete"))
        except:
            outreach_student = None
        form = OutreachForm()
        return render(request, "registration/outreach_form.html", {"form": form, "quarter_token": token})

    if request.method == "POST":
        form = OutreachForm(request.POST)
        if form.is_valid():
            outreach_student = OutreachStudent.objects.filter(user=user.user_id).first()
            # If existing outreach student, just update quarter and info
            if (outreach_student):
                outreach_student.quarter = curr_quarter
                outreach_student.car = form.cleaned_data["car"]
                outreach_student.outreach_course=form.cleaned_data["outreach_course"]
                outreach_student.save()
            # If new outreach student, create a new object
            else:
                user.groups.add(Group.objects.get(name="outreach"))

                outreach_student = OutreachStudent(
                    user=user,
                    car=form.cleaned_data["car"],
                    outreach_course=form.cleaned_data["outreach_course"],
                    quarter=curr_quarter,
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