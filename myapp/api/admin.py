from django.contrib import admin
from myapp.api.models.events import Event, EventType, EventActionRecord
from myapp.api.models.users import CustomUser, Inductee, Member, OutreachStudent, Officer, InductionClass
from myapp.api.models.houses import House, HousePointRecord, HouseMembership
from myapp.api.models.collectibles import CollectibleItem, UserCollectible, DraftRecord


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Event)
admin.site.register(EventActionRecord)
admin.site.register(EventType)
admin.site.register(House)
admin.site.register(HousePointRecord)
admin.site.register(HouseMembership)
admin.site.register(CollectibleItem)
admin.site.register(UserCollectible)
admin.site.register(DraftRecord)
admin.site.register(InductionClass)
admin.site.register(Inductee)
admin.site.register(Member)
admin.site.register(OutreachStudent)
admin.site.register(Officer)