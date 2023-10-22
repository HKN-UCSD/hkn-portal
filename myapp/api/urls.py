from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="event")
router.register(r'eventactionrecords', views.EventActionRecordViewSet, basename='eventrecord')
router.register(r'users', views.UserViewSet, basename="users")
router.register(r'officers', views.OfficerViewSet, basename="officers")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtype")
router.register(r'groups', views.GroupsViewSet, basename="groups")

urlpatterns = [
   path("actions/", views.EventActionView),
   path("eventactionrecords/pair/<int:event_pk>/<str:other_user_id>/", views.EventActionRecordsForEventUserPair),
   path('profile/', views.UserProfileView.as_view(), name="user_profile"),
   path('permissions/', views.PermissionsView)
]

urlpatterns += router.urls

if settings.DEBUG:
    # During development, serve media files locally
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)