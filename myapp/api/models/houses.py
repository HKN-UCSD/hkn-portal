from django.db import models
from django.utils import timezone
from .users import CustomUser
from .events import Event

class House(models.Model):
    name = models.CharField(max_length=65, primary_key=True, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, default="Blue")
    logo = models.CharField(max_length=200, default="/static/HouseLogo.png")

    def __str__(self) -> str:
        return self.name

    @property
    def total_points(self):
        points = HousePointRecord.objects.filter(house=self).aggregate(models.Sum("points")).get('points__sum')
        return points if points else 0


class HousePointRecord(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="point_records")
    points = models.FloatField(default=0)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="house_points_added")
    member = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="house_points_earned")

    def __str__(self) -> str:
        member_name = f"{self.member.first_name} {self.member.last_name}" if self.member else "House"
        return f"{self.house.name}: {self.points} points - {self.description or 'Manual Entry'} ({member_name})"


class HouseMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="members")
    date_joined = models.DateTimeField(default=timezone.now)
    is_house_leader = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} - {self.house.name}"

    @property
    def individual_points(self):
        # Calculate points by summing all point records for this member in this house
        from django.db.models import Sum
        points_sum = HousePointRecord.objects.filter(
            house=self.house,
            member=self.user
        ).aggregate(Sum('points')).get('points__sum')
        return points_sum if points_sum is not None else 0

    class Meta:
        unique_together = ('user', 'house')