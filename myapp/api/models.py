from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class EventType(models.Model):
    name=models.CharField(max_length=255, unique=True)
    edit_groups=models.ManyToManyField(Group, blank=True, related_name="editable_event_types")
    # edit_groups should always be permitted to view.
    view_groups=models.ManyToManyField(Group, blank=True, related_name="viewable_event_types")

    def __str__(self):
        return self.name
    

class Event(models.Model):
    name=models.CharField(max_length=255)
    time_created=models.DateTimeField(auto_now_add=True)
    time_last_modified=models.DateTimeField(auto_now=True)
    description=models.TextField()
    attendees=models.ManyToManyField(User, blank=True)
    event_type=models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)
    
    def __str__(self) -> str:
        return f"({self.pk}) " + str(self.name)

