from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="event")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtype")

urlpatterns = [
     
]

# urlpatterns = format_suffix_patterns([
#     path("", views.RootApi.as_view(), name="root"),
#     path("eventlist", views.EventListApi.as_view(), name="eventlist"),
#     path("eventinstance/<int:pk>", views.EventInstanceApi.as_view(), name="eventinstance"),
# ])

urlpatterns += router.urls