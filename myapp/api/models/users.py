from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from datetime import datetime
import uuid

class Major(models.Model):
    name = models.CharField(max_length=65, primary_key=True, unique=True)

    def __str__(self):
        return self.name


class DegreeLevel(models.Model):
    name = models.CharField(max_length=65, primary_key=True, unique=True)

    def __str__(self):
        return self.name


class InductionClassManager(models.Manager):
    def create_induction_class(self, name, start_date, end_date, academic_year):
        if not (name and start_date and end_date and academic_year):
            raise ValueError("All fields (name, start date, end date, academic year) must be set")
        if not (name and start_date and end_date and academic_year):
            raise ValueError("All fields (name, start date, end date, academic year) must be set")
        induction_class = self.create(
            name=name, start_date=start_date, end_date=end_date, academic_year=academic_year,
        )
        return induction_class


class InductionClass(models.Model):
    name = models.CharField(max_length=65, primary_key=True, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    academic_year = models.IntegerField()
    rollover_event = models.CharField(max_length=65, unique=True, blank=True, null=True)
    form_active = models.BooleanField(default=False)
    rollover_points = models.JSONField(default=dict)
    availabilities = models.JSONField(default=dict) # Adding availabilities
    objects = InductionClassManager()



class QuarterManager(models.Manager):
    def create_quarter(self, name, start_date, end_date, academic_year):
        if not (name and start_date and end_date and academic_year):
            raise ValueError("All fields (name, start date, end date, and academic year) must be set")
        quarter = self.create(
            name=name, start_date=start_date, end_date=end_date, academic_year=academic_year,
        )
        return quarter


class Quarter(models.Model):
    name = models.CharField(max_length=65, primary_key=True, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    academic_year = models.IntegerField()
    objects = QuarterManager()


class CustomUserBase(models.Model):
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    first_name = models.CharField(max_length=65)
    preferred_name = models.CharField(max_length=65)
    middle_name = models.CharField(max_length=65, blank=True, null=True)
    last_name = models.CharField(max_length=65)
    pronouns = models.CharField(max_length=65, blank=True, null=True)
    email = models.EmailField(max_length=65, unique=True)
    major = models.CharField(max_length=65, blank=True, null=True)
    degree = models.CharField(max_length=65, default="Undergraduate")
    grad_year = models.IntegerField(default=datetime.now().year)
    bio = models.CharField(max_length=200, blank=True, null=True)
    induction_class = models.ForeignKey(InductionClass, blank=True, null=True, on_delete=models.SET_NULL)
    profile_picture = models.CharField(max_length=200, default="/static/profile_icons/User.png")
    social_links = models.JSONField(default=
        {
            "instagram": {"icon": "Instagram", "link": "https://www.instagram.com/", "username": ""},
            "linkedin": {"icon": "LinkedIn", "link": "https://www.linkedin.com/in/", "username": ""},
            "github": {"icon": "GitHub", "link": "https://www.github.com/", "username": ""},
        }
    )
    current_courses = models.JSONField(blank=True, default=list)

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
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(default=timezone.now)
    major = models.CharField(max_length=65, blank=True, null=True)
    degree = models.CharField(max_length=65, default="Undergraduate")
    grad_year = models.IntegerField(default=datetime.now().year)

    def __str__(self) -> str:
        if self.user:
            if self.user.induction_class:
                induction_class = self.user.induction_class.name
            else:
                induction_class = "No Class"
            return f"{self.user.first_name} {self.user.last_name} ({induction_class})"
        return "Member"

    @property
    def professional_points(self):
        from myapp.api.models.events import EventActionRecord
        points = EventActionRecord.objects \
                                .filter(event__event_type="Professional", acted_on=self.user, action="Check Off") \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0

    @property
    def social_points(self):
        from myapp.api.models.events import EventActionRecord
        points = EventActionRecord.objects \
                                .filter(event__event_type="Social", acted_on=self.user, action="Check Off") \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0

    @property
    def technical_points(self):
        from myapp.api.models.events import EventActionRecord
        points = EventActionRecord.objects \
                                .filter(event__event_type="Technical", acted_on=self.user, action="Check Off") \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0

    @property
    def outreach_points(self):
        from myapp.api.models.events import EventActionRecord
        points = EventActionRecord.objects \
                                .filter(event__event_type="Outreach", acted_on=self.user, action="Check Off") \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0

    @property
    def mentorship_points(self):
        from myapp.api.models.events import EventActionRecord
        points = EventActionRecord.objects \
                                .filter(event__event_type="Mentorship", acted_on=self.user, action="Check Off") \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0

    @property
    def general_points(self):
        from myapp.api.models.events import EventActionRecord
        points = EventActionRecord.objects \
                                .filter(event__event_type="General", acted_on=self.user, action="Check Off") \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0

    @property
    def total_points(self):
        from myapp.api.models.events import EventActionRecord
        points = EventActionRecord.objects \
                                .filter(acted_on=self.user, action="Check Off") \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0


class Member(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    major = models.CharField(max_length=65, blank=True, null=True)
    degree = models.CharField(max_length=65, default="Undergraduate")
    grad_year = models.IntegerField(default=datetime.now().year)
    current_courses = models.JSONField(blank=True, default=list)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

    @property
    def total_points(self):
        from myapp.api.models.events import EventActionRecord
        cutoff_datetime = timezone.make_aware(datetime(2025, 3, 30))
        points = EventActionRecord.objects \
                                .filter(acted_on=self.user, action="Check Off", event__start_time__gt=cutoff_datetime) \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0

class OutreachStudent(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    car = models.CharField(max_length=65, default="No")
    outreach_course = models.CharField(max_length=65, default="None")
    quarter = models.ForeignKey(Quarter, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

    @property
    def hours(self):
        from myapp.api.models.events import EventActionRecord
        quarter_start_datetime = timezone.make_aware(datetime.combine(self.quarter.start_date, datetime.min.time()))
        points = EventActionRecord.objects \
                                .filter(
                                    event__event_type="Outreach",
                                    acted_on=self.user,
                                    action="Check Off",
                                    event__start_time__gte=quarter_start_datetime,
                                ) \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0


class Officer(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    position = models.CharField(max_length=65, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} ({self.position})"
    
    @property
    def total_points(self):
        from myapp.api.models.events import EventActionRecord
        cutoff_datetime = timezone.make_aware(datetime(2025, 3, 30))
        points = EventActionRecord.objects \
                                .filter(acted_on=self.user, action="Check Off", event__start_time__gt=cutoff_datetime) \
                                .aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0