import os
import image_embedding
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
    SAFE_METHODS,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from myapp.api.serializers import (
    UserSerializer, #TODO: whats the difference between these two?
    CustomUserSerializer, 
    InducteeSerializer, 
    MemberSerializer, 
    OutreachStudentSerializer, 
    OfficerSerializer,
    PermissionGroupSerializer,
    EventActionRecordGetSerializer,
    EventActionRecordPostSerializer,
    EventGetSerializer,
    EventPostSerializer,
    EventTypeSerializer,
)
from myapp.api.models.users import (
    Inductee, 
    Member, 
    OutreachStudent, 
    Officer, 
    CustomUser,
)
from myapp.api.models.events import (
    Event,
    EventActionRecord,
    EventType,
)
from myapp.api.forms import (
    LoginForm,
    RegisterForm,
    InducteeForm,
    OutreachForm,
)
from myapp.api.permissions import HasAdminPermissions, is_admin
from myapp.api import exceptions as act_exceptions
from myapp.api.eventactions import event_action

from django.urls import reverse
from django.http import Http404
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import Group
from django.template.loader import render_to_string

load_dotenv(os.path.join(BASE_DIR, '.env'))

#################################################################
## View Sets
#################################################################
class EventViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return EventGetSerializer
        return EventPostSerializer

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            permission_classes = [HasAdminPermissions]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if is_admin(self.request.user):
            return Event.objects.all()

        user_groups = self.request.user.groups.all()

        if self.request.method in SAFE_METHODS:
            permitted_events_attr = "viewable_events"
            viewable_posts = Event.objects.all().filter(anon_viewable=True)

        for group in user_groups:
            viewable_posts = viewable_posts | getattr(group, permitted_events_attr).all()

        if not is_admin(self.request.user):
            viewable_posts = viewable_posts.filter(is_draft=False)

        return viewable_posts.distinct()

    @action(detail=True, methods=["get"])
    def relevant_users(self, request, pk):
        if not is_admin(self.request.user):
            return Response([])
        else:
            relevant_users = CustomUser.objects.filter(
                actions_received__event__pk=pk
            ).distinct()
        serializer = UserSerializer(relevant_users, many=True)
        if serializer.is_valid:
            return Response(serializer.data)

class EventActionRecordViewSet(ModelViewSet):
    serializer_class = EventActionRecordGetSerializer
    queryset = EventActionRecord.objects.all()
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if is_admin(user):
            return super().get_queryset()

        return super().get_queryset().filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return EventActionRecordGetSerializer
        else:
            return EventActionRecordPostSerializer

    @action(detail=False)
    def get_record_of_action(self, request, action):
        return self.queryset.filter(action=action)

    def create(self, request, *args, **kwargs):
        try:
            serializer = EventActionRecordPostSerializer(data=request.data)
            if serializer.is_valid():
                action = serializer.data["action"]
                event_action.all[action](request, serializer.data)

                return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserViewSet(ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="self")
    def get_self(self, request):
        serializer = UserSerializer(request.user)
        if serializer.is_valid:
            return Response(serializer.data)
        raise act_exceptions.ForbiddenException

class OfficerViewSet(ReadOnlyModelViewSet):
    queryset = CustomUser.objects.filter(groups__name='officer')
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

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
class EventTypeViewSet(ReadOnlyModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class GroupsViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = PermissionGroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

#################################################################
## Specific Views for GET Requests
#################################################################

@api_view(["GET"])
def EventActionRecordsForEventUserPair(request, event_pk, other_user_id):
    serializer = EventActionRecordGetSerializer(
        EventActionRecord.objects.filter(
            event__pk=event_pk, acted_on__user_id=other_user_id
        ),
        many=True,
    )
    if serializer.is_valid:
        return Response(serializer.data)

    raise act_exceptions.ForbiddenException

@api_view(["GET"])
def EventActionView(request):
    permitted_self_actions = []
    permitted_other_actions = []
    for action in event_action.self_actions.keys():
        if (
            action not in event_action.eventless_actions.keys()
        ):
            permitted_self_actions.append(action)

    for action in event_action.other_actions.keys():
        if (
            is_admin(request.user)
            and action not in event_action.eventless_actions.keys()
        ):
            permitted_other_actions.append(action)

    return Response(
        {
            "self_actions": permitted_self_actions,
            "other_actions": permitted_other_actions,
        }
    )


@api_view(["GET"])
def EventlessActionView(request):
    permitted_eventless_actions = []
    for action in event_action.eventless_actons.keys():
        if request.user.has_perm(f"can_{action.lower().replace(' ', '_')}"):
            permitted_eventless_actions.append(action)

    return Response(
        {
            "actions": permitted_eventless_actions,
        }
    )

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
                    'hkn_vector_white': image_embedding.hkn_vector_white,
                }
                email_content = render_to_string('registration/password_reset_email_template.html', context)
                message = Mail(
                    from_email='hkn@ucsd.edu',
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

###
# RPC, functional style calls
###
def email_view():
    raise Http404