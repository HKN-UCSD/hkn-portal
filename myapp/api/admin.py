from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from myapp.api.models.events import Event, EventType, EventActionRecord
from myapp.api.models.users import CustomUser, Inductee, Member, OutreachStudent, Officer, InductionClass


# Register your models here.
admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(EventActionRecord)
admin.site.register(CustomUser)
admin.site.register(InductionClass)
admin.site.register(Inductee)
admin.site.register(Member)
admin.site.register(OutreachStudent)
admin.site.register(Officer)