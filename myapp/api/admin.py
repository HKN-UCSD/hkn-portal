from django.contrib import admin
from .models.events import Event, EventType
from .models.users import CustomUser

# Register your models here.
admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(CustomUser)