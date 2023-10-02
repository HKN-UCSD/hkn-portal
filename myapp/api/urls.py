from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="event")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtype")

urlpatterns = [
   path('profile/', views.UserProfileView.as_view(), name="user_profile"),
]

urlpatterns += router.urls