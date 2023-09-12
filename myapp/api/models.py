from django.db import models
from django.contrib.auth.models import AbstractUser, Group
import uuid

# Create your models here.
class CustomUser(AbstractUser):
    username = None
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    preferred_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    groups = models.ManyToManyField(
        'auth.Group',
         verbose_name='groups',
         blank=True,
         related_name='customuser_groups',
         related_query_name='user'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_permissions',
        related_query_name='user'
    )


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
    attendees=models.ManyToManyField(CustomUser, blank=True)
    event_type=models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)
    
    def __str__(self) -> str:
        return f"({self.pk}) " + str(self.name)

