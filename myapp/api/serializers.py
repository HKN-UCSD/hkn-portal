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
    time_created = DateTimeField()
    time_last_modified = DateTimeField()

    class Meta:
        model = Event
        fields = [
            "pk",
            "name",
            "start_time",
            "end_time",
            "location",
            "hosts",
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
            "user",
            "event",
            "acted_on",
            "action",
            "action_time",
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