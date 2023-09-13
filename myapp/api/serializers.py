from rest_framework.serializers import ModelSerializer
from . import models
from django.contrib.auth.models import AbstractUser


class EventSerializer(ModelSerializer):
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
            "attendees",
            "event_type",
            "edit_groups",
            "view_groups",
            "anon_viewable",
        ]


class PublicEventSerializer(ModelSerializer):
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
        depth=1
    


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = models.EventType
        fields = ["name"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = AbstractUser
        fields = ["username"]
