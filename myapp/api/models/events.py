from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group
from .users import CustomUser
from rest_framework.permissions import IsAuthenticated

class EventType(models.Model):
    name = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)
    time_last_modified = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, blank=True)
    hosts = models.ManyToManyField(CustomUser, blank=True)
    points = models.FloatField(default=1)
    description = models.TextField(blank=True)
    is_draft = models.BooleanField(default=True)
    embed_code = models.TextField(blank=True)

    # Replace start/end times with more sensible defaults
    is_time_restricted = models.BooleanField(default=True)
    start_time = models.DateTimeField(default=timezone.now, blank=True, null=True)
    end_time = models.DateTimeField(default=timezone.now, blank=True, null=True)

    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)

    view_groups = models.ManyToManyField(
        Group, blank=True, related_name="viewable_events"
    )
    anon_viewable = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"({self.pk}) " + str(self.name)

    class Meta:
        permissions = [
            ("can_view_draft", "Can view drafts of events"),
            ("can_view_relevant_users", "Can view all users involved with an event, not just oneself")
        ]


class EventActionRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="actions_taken")
    acted_on = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="actions_received", default=None, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    action_time = models.DateTimeField(auto_now_add=True)
    action = models.TextField(choices=[(key, key)for key in ["RSVP", "Sign In", "Check Off"]], null=True, blank=True) #TODO: Is there a better way to do this
    details = models.TextField(blank=True)
    points = models.FloatField(default=0)

    def default_extra_data():
        return {}

    extra_data = models.JSONField(default=default_extra_data)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["acted_on", "event", "action"],
                name="unique_action_per_user_event_pair",
            )
        ]