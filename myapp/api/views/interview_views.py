"""
Views for interview-related activity
"""
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from myapp.api.models.interviews import InterviewAvailability, InterviewCycle
from myapp.api.permissions import HasAdminPermissions, is_admin
from myapp.api.serializers import BaseInterviewCycleSerializer, BaseInterviewAvailabilitySerializer, OfficerInterviewCycleSerializer

from django_filters.rest_framework import DjangoFilterBackend


class InterviewCycleListView(ListCreateAPIView):
    """
    View for /api/induction_cycle
    """
    queryset = InterviewCycle.objects.all()

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            permission_classes = [HasAdminPermissions]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return OfficerInterviewCycleSerializer if is_admin(self.request.user) else BaseInterviewCycleSerializer


class InterviewCycleView(RetrieveDestroyAPIView):
    """
    View for /api/induction_cycle/<cycle_id>
    """
    queryset = InterviewCycle.objects.all()

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            permission_classes = [HasAdminPermissions]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return OfficerInterviewCycleSerializer if is_admin(self.request.user) else BaseInterviewCycleSerializer


class InterviewAvailabilityListView(ListCreateAPIView):
    """
    View for /api/interviewavailabilities
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["interview_cycle"]

    def get_queryset(self):
        # TODO: retrict queryset based on permissions
        user = self.request.user
        interview_cycle = self.request.query_params.get("interview_cycle")
        kwargs = {}

        if not is_admin(user):
            kwargs["user_id"] = user.pk

        if interview_cycle is not None:
            kwargs["interview_cycle_id"] = interview_cycle

        return InterviewAvailability.objects.filter(**kwargs)
        # if is_admin(user):
        #     return InterviewAvailability.objects.all(**kwargs)
        # else:
        #     return InterviewAvailability.objects.filter(**kwargs)

    def get_serializer_class(self):
        return BaseInterviewAvailabilitySerializer


class InterviewAvailabilityView(RetrieveUpdateAPIView):
    """
    View for /api/interviewavailabilities/<availability_id>
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["interview_cycle"]

    def get_queryset(self):
        # TODO: retrict queryset based on permissions
        user = self.request.user
        if is_admin(user):
            return InterviewAvailability.objects.all()
        else:
            return InterviewAvailability.objects.filter(user=user.pk)

    def get_serializer_class(self):
        return BaseInterviewAvailabilitySerializer
