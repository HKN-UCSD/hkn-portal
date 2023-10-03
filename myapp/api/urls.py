from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="event")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtype")
router.register(r'eventactionrecords', views.EventActionRecordViewSet, basename='eventrecord')
router.register(r'users', views.UserViewSet, basename="users")
router.register(r'officers', views.OfficerViewSet, basename="officers")
router.register(r'permission_groups', views.PermissionGroupsViewSet, basename="permission_groups")

urlpatterns = [
   path("actions/", views.EventActionView),
   path("eventactionrecords/pair/<int:event_pk>/<str:other_user_id>/", views.EventActionRecordsForEventUserPair),
   path('profile/', views.UserProfileView.as_view(), name="user_profile"),
   path('event_permissions/', views.EventPermissionsView)
]

urlpatterns += router.urls