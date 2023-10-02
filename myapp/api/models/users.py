from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
import uuid

class CustomUserBase(models.Model):
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    first_name = models.CharField(max_length=65)
    middle_name = models.CharField(max_length=65, blank=True, null=True)
    last_name = models.CharField(max_length=65)
    email = models.EmailField(max_length=65, unique=True)

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        related_name="customuser_groups",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        related_name="customuser_permissions",
        related_query_name="user",
    )

    class Meta:
        abstract = True


class CustomUserManager(UserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser, CustomUserBase):
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    email = models.EmailField(max_length=65, unique=True)
    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.email})"


class Inductee(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    preferred_name = models.CharField(max_length=65, blank=True, null=True)
    major = models.CharField(max_length=65, blank=True, null=True)
    degree = models.CharField(max_length=65, default="Undergraduate")
    grad_year = models.IntegerField(default=datetime.datetime.now().year)
    professional_points = models.IntegerField(default=0)
    social_points = models.IntegerField(default=0)
    technical_points = models.IntegerField(default=0)
    outreach_points = models.IntegerField(default=0)
    mentorship_points = models.IntegerField(default=0)
    general_points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)


class Member(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    preferred_name = models.CharField(max_length=65, blank=True, null=True)
    major = models.CharField(max_length=65, null=True)
    degree = models.CharField(max_length=65, default="Undergraduate")
    grad_year = models.IntegerField(default=datetime.datetime.now().year)


class OutreachStudent(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    car = models.CharField(max_length=65, default="No")
    outreach_course = models.CharField(max_length=65, default="None")
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)


class Officer(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    position = models.CharField(max_length=65, blank=True, null=True)


class Admin(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)


