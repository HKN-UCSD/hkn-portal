from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="event")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtype")
router.register(r'eventactionrecords', views.EventActionRecordViewSet, basename='eventrecord')
router.register(r'users', views.UserViewSet, basename="users")

urlpatterns = []

urlpatterns += router.urls