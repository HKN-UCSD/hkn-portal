from django.db import models
from django.utils import timezone
from .users import CustomUser

class CollectibleItem(models.Model):
    """Model for collectible item definitions"""
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    TYPE_CHOICES = [
        ('icon', 'Profile Icon'),
        ('frame', 'Avatar Frame'),
        ('banner', 'Profile Banner'),
        ('badge', 'Badge'),
        ('theme', 'UI Theme'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField()
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_seasonal = models.BooleanField(default=False)
    season = models.CharField(max_length=20, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class UserCollectible(models.Model):
    """Model for tracking which collectibles a user has"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="collectibles")
    item = models.ForeignKey(CollectibleItem, on_delete=models.CASCADE)
    is_equipped = models.BooleanField(default=False)
    equipped_slot = models.CharField(max_length=20, blank=True, null=True)
    acquired_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "item"],
                name="unique_user_collectible",
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.item.name}"


class DraftRecord(models.Model):
    """Model for tracking drafts and available draft tokens"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="drafts")
    available_drafts = models.IntegerField(default=0)
    last_calculated = models.DateTimeField(default=timezone.now)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                name="unique_user_draft_record",
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.available_drafts} drafts" 