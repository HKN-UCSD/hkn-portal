from rest_framework.serializers import ModelSerializer
from rest_framework.fields import DateTimeField
from . import models
from django.contrib.auth.models import AbstractUser


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
        fields = ["name"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = ["username"]
