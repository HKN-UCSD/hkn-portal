from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from myapp.api.models.events import Event, EventType, EventActionRecord
from myapp.api.models.users import CustomUser
from myapp.api.eventactions import event_action
from myapp.api.serializers import (
    EventActionRecordGetSerializer,
    EventGetSerializer,
    EventPostSerializer,
    EventActionRecordPostSerializer,
    UserSerializer,
    EventTypeSerializer,
)
from myapp.api.permissions import HasAdminPermissions, is_admin
from myapp.api import exceptions as act_exceptions

class EventViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return EventGetSerializer
        return EventPostSerializer

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            permission_classes = [HasAdminPermissions]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Overrides the original get_queryset(which simply allows all events to be
        seen by whoever made a GET request). This version takes the set of all
        posts viewable by each group a user is in, and unions them together.
        Essentially, if a user is in even a single group that can view an event,
        they will see that event.

        Once the list of events has been compiled, we also filter out draft posts,
        unless the user is an officer/admin.
        """

        if is_admin(self.request.user):
            return Event.objects.all()

        user_groups = self.request.user.groups.all()

        if self.request.method in SAFE_METHODS:
            permitted_events_attr = "viewable_events"
            viewable_posts = Event.objects.all().filter(anon_viewable=True)

        for group in user_groups:
            viewable_posts = (
                viewable_posts | getattr(group, permitted_events_attr).all()
            )

        if not is_admin(self.request.user):
            viewable_posts = viewable_posts.filter(is_draft=False)

        return viewable_posts.distinct()

    @action(detail=True, methods=["get"])
    def relevant_users(self, request, pk):
        if not is_admin(self.request.user):
            return Response([])
        else:
            relevant_users = CustomUser.objects.filter(
                actions_received__event__pk=pk
            ).distinct()
        serializer = UserSerializer(relevant_users, many=True)
        if serializer.is_valid:
            return Response(serializer.data)


class EventTypeViewSet(ReadOnlyModelViewSet):
    """
    Provides read-only access to Event Types. As of now, adding event types must
    be done by accessing the server being deployed on and using the command line.
    """

    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EventActionRecordViewSet(ModelViewSet):
    """
    For admins, provides access to all records of guest/member activity.
    For users, provides access to their own records.
    All users can attempt to post any event action, but filtering based on permissions
    or other criteria can be done in eventactions.py.
    """

    serializer_class = EventActionRecordGetSerializer
    queryset = EventActionRecord.objects.all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        eventid = self.request.GET.get('eventid')
        qs = super().get_queryset()
        if eventid is None:
            if is_admin(user):
                return qs

            return qs.filter(acted_on=self.request.user)
        else:
            if is_admin(user):
                return qs.filter(event__pk = eventid)

            return qs.filter(acted_on=self.request.user, event__pk = eventid)

    def destroy(self, request, *args, **kwargs):
        # TODO: remove users' ability to check themselves off
        record = self.get_object()
        if (request.user.pk == record.user.pk or
            request.user.pk == record.acted_on.pk or
            is_admin(request.user)):
            self.perform_destroy(record)
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise act_exceptions.ForbiddenException("Delete forbidden: Not the "
                                                "originator or receiver of the "
                                                "action, and not an admin")

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return EventActionRecordGetSerializer
        else:
            return EventActionRecordPostSerializer

    """
    In response to an approporiate POST request to /api/eventactionrecords/,
    creates a new EventActionRecord.
    """

    def create(self, request, *args, **kwargs):
        try:
            serializer = EventActionRecordPostSerializer(data=request.data)
            if serializer.is_valid():
                action = serializer.data["action"]
                event_action.all[action](request, serializer.data)

                return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    """
    The original perform_create saves the serializer as-is, but when receiving a
    POST request the serializer doesn't store information about the action's
    performer. This perform_create
    overrides the original, attaching the user who made the request to the
    event action record as the performer of the action.
    """

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["GET"])
def EventActionRecordsForEventUserPair(request, event_pk, other_user_id):
    serializer = EventActionRecordGetSerializer(
        EventActionRecord.objects.filter(
            event__pk=event_pk, acted_on__user_id=other_user_id
        ),
        many=True,
    )
    if serializer.is_valid:

        return Response(serializer.data)

    raise act_exceptions.ForbiddenException

@api_view(["GET"])
def EventActionRecordsForUser(request,user_id):
    serializer = EventActionRecordGetSerializer(
        EventActionRecord.objects.filter(
            acted_on__user_id=user_id
        ),
        many=True,
    )
    if serializer.is_valid:

        return Response(serializer.data)

    raise act_exceptions.ForbiddenException


@api_view(["GET"])
def EventActionView(request):
    permitted_self_actions = []
    permitted_other_actions = []
    for action in event_action.self_actions.keys():
        if action not in event_action.eventless_actions.keys():
            permitted_self_actions.append(action)

    for action in event_action.other_actions.keys():
        if (
            is_admin(request.user)
            and action not in event_action.eventless_actions.keys()
        ):
            permitted_other_actions.append(action)

    return Response(
        {
            "self_actions": permitted_self_actions,
            "other_actions": permitted_other_actions,
        }
    )


@api_view(["GET"])
def EventlessActionView(request):
    permitted_eventless_actions = []
    for action in event_action.eventless_actons.keys():
        if request.user.has_perm(f"can_{action.lower().replace(' ', '_')}"):
            permitted_eventless_actions.append(action)

    return Response(
        {
            "actions": permitted_eventless_actions,
        }
    )