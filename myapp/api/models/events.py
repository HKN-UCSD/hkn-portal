from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group
from myapp.api.eventactions import event_action
from .users import CustomUser

class EventType(models.Model):
    name = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)
    time_last_modified = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, blank=True)
    hosts = models.ManyToManyField(CustomUser)
    points = models.FloatField(default=1)
    description = models.TextField(blank=True)
    is_draft = models.BooleanField(default=True)

    # Replace start/end times with more sensible defaults
    start_time = models.DateTimeField(default=timezone.now, blank=True, null=True)
    end_time = models.DateTimeField(default=timezone.now, blank=True, null=True)

    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)

    edit_groups = models.ManyToManyField(
        Group, blank=True, related_name="editable_events"
    )
    # edit_groups should always be permitted to view.
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
    action = models.TextField(choices=[(key, key)for key in event_action.all.keys()], null=True, blank=True)
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

        permissions = [(f"can_{action_name.replace(' ', '_').lower()}", action_name) for action_name in event_action.all.keys()]