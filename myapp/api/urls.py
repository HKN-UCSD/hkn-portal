from django.urls import path, include
from rest_framework import routers
from django.conf.urls.static import static
from django.conf import settings
from myapp.api.views import event_views, user_views, house_views, collectible_views

router = routers.DefaultRouter()
router.register(r'eventactionrecords', event_views.EventActionRecordViewSet, basename='eventrecord')
router.register(r'events', event_views.EventViewSet, basename="event")
router.register(r'eventtypes', event_views.EventTypeViewSet, basename="eventtype")
router.register(r'groups', user_views.GroupsViewSet, basename="groups")
router.register(r'users', user_views.UserViewSet, basename="users")
router.register(r'majors', user_views.MajorViewSet, basename="major")
router.register(r'degreelevel', user_views.DegreeLevelViewSet, basename="degree")
router.register(r'profile', user_views.UserProfileViewSet, basename="profile")
router.register(r'inductees', user_views.InducteeViewSet, basename="inductees")
router.register(r'members', user_views.MemberViewSet, basename="members")
router.register(r'inductionclasses', user_views.InductionClassViewSet, basename="inductionclass")
router.register(r'outreach', user_views.OutreachViewSet, basename="outreach")
router.register(r'officers', user_views.OfficerViewSet, basename="officers")
router.register(r'leaderboard', user_views.LeaderBoardViewSet, basename="leaderboard")
router.register(r'houses', house_views.HouseViewSet, basename="houses")
router.register(r'house-points', house_views.HousePointRecordViewSet, basename="house-points")
router.register(r'house-memberships', house_views.HouseMembershipViewSet, basename="house-memberships")
router.register(r'collectibles/items', collectible_views.CollectibleViewSet, basename="collectibles")
router.register(r'collectibles/user', collectible_views.UserCollectibleViewSet, basename="user-collectibles")
router.register(r'collectibles/drafts', collectible_views.DraftRecordViewSet, basename="draft-records")

urlpatterns = [
   path("actions/", event_views.EventActionView),
   path("eventactionrecords/pair/<int:event_pk>/<str:other_user_id>/", event_views.EventActionRecordsForEventUserPair),
   path("eventactionrecords/user/<str:user_id>/", event_views.EventActionRecordsForUser),
   path('permissions/', user_views.PermissionsView),
   path('house/user/', house_views.get_user_house),
   path('house/leaderboard/', house_views.get_house_leaderboard),
   path('house/members/<str:house_name>/', house_views.get_house_members_leaderboard),
   path('house/history/<str:house_name>/', house_views.get_house_points_history),
   path('house/add-member-points/<str:user_id>/', house_views.add_member_points),
   path('house/edit-point-record/<int:record_id>/', house_views.edit_point_record),
   path('house/delete-point-record/<int:record_id>/', house_views.delete_point_record),
   
   # Collectibles endpoints
   path('collectibles/', collectible_views.get_collectibles_home_data),
   path('collectibles/get-drafts-data/', collectible_views.get_drafts_data),
   path('collectibles/perform-draft/', collectible_views.perform_draft),
   path('collectibles/catalog/', collectible_views.get_catalog_data),
   path('collectibles/loadout/', collectible_views.get_loadout_data),
   path('collectibles/<int:collectible_id>/equip/', collectible_views.equip_collectible),
   path('collectibles/add/', collectible_views.add_collectible),
   path('collectibles/delete/<int:collectible_id>/', collectible_views.delete_collectible),
]

urlpatterns += router.urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)