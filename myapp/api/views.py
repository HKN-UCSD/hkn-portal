from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import connection
from django.core.exceptions import SuspiciousOperation
from django.db.models import Q
from . import models, serializers


class EventViewSet(ModelViewSet):
    serializer_class = serializers.PublicEventSerializer

    # TODO: replace with Django REST permissions
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Event.objects.all()

        user_groups = self.request.user.groups.all()
        all_event_types = models.EventType.objects.all()

        if self.request.method == "GET":
            permitted_event_types = [
                event_type
                for event_type in all_event_types
                if event_type.view_groups.intersection(user_groups)
            ]
        elif self.request.method in ["POST", "PUT", "DELETE"]:
            permitted_event_types = [
                event_type
                for event_type in all_event_types
                if event_type.edit_groups.intersection(user_groups)
            ]
        else:
            raise SuspiciousOperation

        permitted_events = models.Event.objects.all().filter(
            event_type__in=permitted_event_types
        )
        return permitted_events


class EventTypeViewSet(ModelViewSet):
    queryset = models.EventType.objects.all()
    serializer_class = serializers.EventTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RootApi(APIView):
    def get(self, request, format=None):
        return Response(
            {
                "eventlist": reverse("eventlist", request=request, format=format),
                "eventinstance": reverse(
                    "eventinstance", request=request, format=format, kwargs={"pk": 0}
                ),
            }
        )
