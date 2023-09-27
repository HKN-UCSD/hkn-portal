from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename="events")
router.register(r'eventtypes', views.EventTypeViewSet, basename="eventtypes")
router.register(r'eventactions', views.EventActionViewSet, basename="eventactions")
router.register(r'eventactionrecords', views.UniqueActionEventViewSet, basename='eventrecords')
router.register(r'users', views.UserViewSet, basename="users")

urlpatterns = [
    path("events/action/<int:pk>/", views.EventHandleActionView),
    path("events/interface/<str:interface_name>/", views.EventInterfaceView)
]

urlpatterns += router.urls