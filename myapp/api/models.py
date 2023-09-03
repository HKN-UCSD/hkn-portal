from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
import uuid

class CustomUser(AbstractUser):
    username = None
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)
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

class Member(CustomUser):
    middle_name = models.CharField(max_length=65, blank=True, null=True)
    preferred_name = models.CharField(max_length=65, blank=True, null=True)
    major = models.CharField(max_length=65)
    grad_year = models.IntegerField(default=datetime.datetime.now().year)

    @receiver(post_save, sender=CustomUser)
    def create_member(sender, instance, created, **kwargs):
        if created:
            Member.objects.create(user=instance)

    @receiver(post_save, sender=CustomUser)
    def save_member(sender, instance, **kwargs):
        try:
            instance.member.save()
        except Member.DoesNotExist:
            pass

class Inductee(Member):
    points = models.IntegerField(default=0)

    @receiver(post_save, sender=Member)
    def create_inductee(sender, instance, created, **kwargs):
        if created:
            Inductee.objects.create(member=instance)
    
    @receiver(post_save, sender=Member)
    def save_inductee(sender, instance, **kwargs):
        try:
            instance.inductee.save()
        except Inductee.DoesNotExist:
            pass

class OutreachStudent(models.Model):
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
