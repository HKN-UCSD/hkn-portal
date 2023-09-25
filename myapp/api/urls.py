from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="event")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtype")
router.register(r'eventactions', views.EventActionViewSet, basename="eventaction")

urlpatterns = [
    path("events/action/<int:pk>/", views.EventHandleActionView),
]

urlpatterns += router.urls