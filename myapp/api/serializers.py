from rest_framework.serializers import ModelSerializer
from rest_framework.fields import DateTimeField
from .models.users import CustomUser
from .models.events import Event, EventActionRecord, EventType


class EventGetSerializer(ModelSerializer):
    start_time = DateTimeField()
    end_time = DateTimeField()
    time_created = DateTimeField()
    time_last_modified = DateTimeField()

    class Meta:
        model = Event
        fields = [
            "pk",
            "name",
            "time_created",
            "time_last_modified",
            "start_time",
            "end_time",
            "location",
            "hosts",
            "points",
            "description",
            "event_type",
            "edit_groups",
            "view_groups",
            "anon_viewable",
            "is_draft",
        ]


class EventPostSerializer(ModelSerializer):
    start_time = DateTimeField()
    end_time = DateTimeField()

    class Meta:
        model = Event
        fields = [
            "pk",
            "name",
            "start_time",
            "end_time",
            "location",
            "hosts",
            "points",
            "description",
            "event_type",
            "edit_groups",
            "view_groups",
            "anon_viewable",
            "is_draft",
        ]


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = EventType
        fields = ["name"]


class EventActionSerializer(ModelSerializer):
    class Meta:
        model = EventActionRecord
        fields = ["name"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["user_id", "first_name", "last_name", "email"]


class EventActionRecordGetSerializer(ModelSerializer):
    class Meta:
        model = EventActionRecord
        fields = [
            "pk",
            "user",
            "event",
            "acted_on",
            "action",
            "action_time",
            "points",
            "details",
            "extra_data",
        ]

class EventActionRecordPostSerializer(ModelSerializer):
    class Meta:
        model = EventActionRecord
        fields = [
            "event",
            "acted_on",
            "action",
            "details",
            "extra_data",
        ]


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "pronouns",
        ]


class InducteeSerializer(ModelSerializer):
    class Meta:
        model = Inductee
        fields = [
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
            "preferred_name",
            "major",
            "degree",
            "grad_year",
        ]


class OutreachStudentSerializer(ModelSerializer):
    class Meta:
        model = OutreachStudent
        fields = [
            "car",
            "outreach_course",
            "hours",
        ]


class OfficerSerializer(ModelSerializer):
    class Meta:
        model = Officer
        fields = [
            "position",
        ]