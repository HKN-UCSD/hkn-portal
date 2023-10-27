from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="event")
router.register(r'eventactionrecords', views.EventActionRecordViewSet, basename='eventrecord')
router.register(r'users', views.UserViewSet, basename="users")
router.register(r'officers', views.OfficerViewSet, basename="officers")
router.register(r'inductees', views.InducteeViewSet, basename="inductees")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtype")
router.register(r'groups', views.GroupsViewSet, basename="groups")

urlpatterns = [
   path("actions/", views.EventActionView),
   path("eventactionrecords/pair/<int:event_pk>/<str:other_user_id>/", views.EventActionRecordsForEventUserPair),
   path('profile/', views.UserProfileView.as_view(), name="user_profile"),
   path('permissions/', views.PermissionsView)
]

urlpatterns += router.urls