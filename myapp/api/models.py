from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
import uuid

class CustomUserBase(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=65)
    middle_name = models.CharField(max_length=65, blank=True, null=True)
    last_name = models.CharField(max_length=65)
    email = models.EmailField(max_length=65, unique=True)

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

    class Meta:
        abstract = True

class CustomUser(AbstractUser, CustomUserBase):
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    email = models.EmailField(max_length=65, unique=True)

class Member(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    preferred_name = models.CharField(max_length=65, blank=True, null=True)
    major = models.CharField(max_length=65, null=True)
    grad_year = models.IntegerField(default=datetime.datetime.now().year)

class Inductee(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    preferred_name = models.CharField(max_length=65, blank=True, null=True)
    major = models.CharField(max_length=65, null=True)
    grad_year = models.IntegerField(default=datetime.datetime.now().year)
    points = models.IntegerField(default=0)

class OutreachStudent(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
