from rest_framework.serializers import ModelSerializer, FloatField
from rest_framework.fields import DateTimeField
from django.db.models import JSONField
from myapp.api.models.users import CustomUser, Inductee, Member, Officer, OutreachStudent, InductionClass, Major, DegreeLevel
from myapp.api.models.events import Event, EventActionRecord, EventType
from django.contrib.auth.models import Group


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
            "is_time_restricted",
            "time_created",
            "time_last_modified",
            "start_time",
            "end_time",
            "location",
            "hosts",
            "points",
            "description",
            "event_type",
            "view_groups",
            "anon_viewable",
            "is_draft",
            "embed_code",
            "rides",
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
            "is_time_restricted",
            "location",
            "hosts",
            "points",
            "description",
            "event_type",
            "view_groups",
            "anon_viewable",
            "is_draft",
            "embed_code",
            "rides",
        ]


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = EventType
        fields = ["name"]


class MajorSerializer(ModelSerializer):
    class Meta:
        model = Major
        fields = ["name"]


class DegreeLevelSerializer(ModelSerializer):
    class Meta:
        model = DegreeLevel
        fields = ["name"]
        

class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "first_name",
            "preferred_name",
            "last_name",
            "email",
            "is_superuser",
        ]


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
            "points"
        ]


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "email",
            "first_name",
            "preferred_name",
            "middle_name",
            "last_name",
            "induction_class",
            "pronouns",
        ]


class InducteeSerializer(ModelSerializer):
    professional_points = FloatField(read_only=True, default=0.0)
    social_points = FloatField(read_only=True, default=0.0)
    technical_points = FloatField(read_only=True, default=0.0)
    outreach_points = FloatField(read_only=True, default=0.0)
    mentorship_points = FloatField(read_only=True, default=0.0)
    general_points = FloatField(read_only=True, default=0.0)
    total_points = FloatField(read_only=True, default=0.0)
    availability = JSONField()
    

    class Meta:
        model = Inductee
        fields = [
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
            "major",
            "degree",
            "grad_year",
        ]


class OutreachStudentSerializer(ModelSerializer):
    hours = FloatField(read_only=True, default=0.0)
    class Meta:
        model = OutreachStudent
        fields = [
            "car",
            "quarter",
            "outreach_course",
            "hours",
        ]


class OfficerSerializer(ModelSerializer):
    class Meta:
        model = Officer
        fields = [
            "position",
        ]


class InductionClassSerializer(ModelSerializer):
    class Meta:
        model = InductionClass
        fields = [
            "name",
            "start_date",
            "end_date",
            "academic_year",
            "rollover_points",
            "availabilities"
        ]

class PermissionGroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'name',
        ]
