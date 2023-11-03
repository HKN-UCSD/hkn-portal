from django.urls import path
from rest_framework.routers import DefaultRouter
from myapp.api.views import views, event_views

router = DefaultRouter()
router.register(r'events', event_views.EventViewSet, basename="event")
router.register(r'eventactionrecords', event_views.EventActionRecordViewSet, basename='eventrecord')
router.register(r'users', views.UserViewSet, basename="users")
router.register(r'officers', views.OfficerViewSet, basename="officers")
router.register(r'eventtypes', event_views.EventTypeViewSet, basename="eventtype")
router.register(r'groups', views.GroupsViewSet, basename="groups")

urlpatterns = [
   path("actions/", event_views.EventActionView),
   path("eventactionrecords/pair/<int:event_pk>/<str:other_user_id>/", event_views.EventActionRecordsForEventUserPair),
   path('profile/', views.UserProfileView.as_view(), name="user_profile"),
   path('permissions/', views.PermissionsView)
]

urlpatterns += router.urls