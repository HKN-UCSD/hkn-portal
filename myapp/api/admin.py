from django.contrib import admin
from myapp.api.models.events import Event, EventType, EventActionRecord
from myapp.api.models.users import CustomUser, InductionClass

# Register your models here.
admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(EventActionRecord)
admin.site.register(CustomUser)
admin.site.register(InductionClass)
