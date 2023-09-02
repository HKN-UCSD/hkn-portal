from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class CustomUser(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

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

class Inductee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

class OutreachStudent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
