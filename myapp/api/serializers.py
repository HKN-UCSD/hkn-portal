from rest_framework.serializers import ModelSerializer
from rest_framework.fields import DateTimeField
from . import models
from .models import CustomUser, Inductee, Member, OutreachStudent, Officer, Admin


class EventSerializer(ModelSerializer):
    start_time = DateTimeField()
    end_time = DateTimeField()
    time_created = DateTimeField()
    time_last_modified = DateTimeField()

    class Meta:
        model = models.Event
        fields = [
            "pk",
            "name",
            "description",
            "attendees",
            "event_type",
            "edit_groups",
            "view_groups",
            "anon_viewable",
        ]


class PublicEventSerializer(ModelSerializer):
    # event_type
    # edit_groups
    # view_groups
    class Meta:
        model = models.Event
        fields = [
            "pk",
            "name",
            "time_created",
            "time_last_modified",
            "start_time",
            "end_time",
            "description",
            "event_type",
            "edit_groups",
            "view_groups",
            "anon_viewable",
        ]


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = models.EventType
        fields = ["pk", "name"]


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "pronouns",
        ]


class InducteeSerializer(ModelSerializer):
    class Meta:
        model = Inductee
        fields = [
            "user",
            "preferred_name",
            "major",
            "degree",
            "grad_year",
            "professional_points",
            "social_points",
            "technical_points",
            "outreach_points",
            "mentorship_points",
            "general_points",
            "total_points",
        ]


class MemberSerializer(ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "user",
            "preferred_name",
            "major",
            "degree",
            "grad_year",
        ]


class OutreachStudentSerializer(ModelSerializer):
    class Meta:
        model = OutreachStudent
        fields = [
            "user",
            "car",
            "outreach_course",
            "hours",
        ]


class OfficerSerializer(ModelSerializer):
    class Meta:
        model = Officer
        fields = [
            "user",
            "position",
        ]