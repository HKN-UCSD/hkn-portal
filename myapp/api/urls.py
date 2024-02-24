from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static
from myapp.api.views import event_views, user_views

router = DefaultRouter()
router.register(r'eventactionrecords', event_views.EventActionRecordViewSet, basename='eventrecord')
router.register(r'events', event_views.EventViewSet, basename="event")
router.register(r'eventtypes', event_views.EventTypeViewSet, basename="eventtype")

router.register(r'groups', user_views.GroupsViewSet, basename="groups")
router.register(r'users', user_views.UserViewSet, basename="users")
router.register(r'majors', user_views.MajorViewSet, basename="major")
router.register(r'degreelevel', user_views.DegreeLevelViewSet, basename="degree")
router.register(r'profile', user_views.UserProfileViewSet, basename="profile")
router.register(r'inductees', user_views.InducteeViewSet, basename="inductees")
router.register(r'inductionclasses', user_views.InductionClassViewSet, basename="inductionclass")
router.register(r'outreach', user_views.OutreachViewSet, basename="outreach")
router.register(r'officers', user_views.OfficerViewSet, basename="officers")


urlpatterns = [
   path("actions/", event_views.EventActionView),
   path("eventactionrecords/pair/<int:event_pk>/<str:other_user_id>/", event_views.EventActionRecordsForEventUserPair),
   path('permissions/', user_views.PermissionsView)
]

urlpatterns += router.urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)