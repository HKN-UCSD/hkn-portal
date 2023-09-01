from rest_framework.serializers import ModelSerializer
from . import models
from django.contrib.auth.models import User


class EventSerializer(ModelSerializer):
    class Meta:
        model = models.Event
        fields = [
            "pk",
            "name",
            "time_created",
            "time_last_modified",
            "description",
            "attendees",
            "event_type",
        ]


class PublicEventSerializer(ModelSerializer):
    class Meta:
        model = models.Event
        fields = [
            "pk",
            "name",
            "time_created",
            "time_last_modified",
            "description",
            "event_type",
        ]


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = models.EventType
        fields = ["name"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]
