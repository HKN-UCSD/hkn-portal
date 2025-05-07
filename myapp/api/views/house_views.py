from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count

from myapp.api.models.houses import House, HousePointRecord, HouseMembership
from myapp.api.models.users import CustomUser
from myapp.api.serializers import HouseSerializer, HousePointRecordSerializer, HouseMembershipSerializer, EventActionRecordPostSerializer
from myapp.api.permissions import IsStaffOrReadOnly, IsHouseLeaderOrReadOnly, IsHouseLeaderOfMember, is_admin


class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsStaffOrReadOnly]


class HousePointRecordViewSet(viewsets.ModelViewSet):
    queryset = HousePointRecord.objects.all().order_by('-date_added')
    serializer_class = HousePointRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsHouseLeaderOrReadOnly]

    def get_queryset(self):
        queryset = HousePointRecord.objects.all().order_by('-date_added')
        house = self.request.query_params.get('house', None)
        if house is not None:
            queryset = queryset.filter(house__name=house)
        return queryset

    def perform_create(self, serializer):
        # Set the added_by field to the current user
        serializer.save(added_by=self.request.user)

    def perform_update(self, serializer):
        # Only allow the user who added the points or an admin to edit them
        record = self.get_object()
        if not is_admin(self.request.user) and record.added_by != self.request.user:
            raise permissions.PermissionDenied("You can only edit point records that you added.")

        # Get the original points value
        original_points = record.points
        # Get the new points value
        new_points = float(self.request.data.get('points', original_points))
        # Calculate the difference
        points_difference = new_points - original_points

        # Update the member's individual points if there's a member associated
        if record.member and points_difference != 0:
            try:
                membership = HouseMembership.objects.get(user=record.member, house=record.house)
                membership.points += points_difference
                membership.save()
            except HouseMembership.DoesNotExist:
                pass

        serializer.save()

    def perform_destroy(self, instance):
        # Only allow the user who added the points or an admin to delete them
        if not is_admin(self.request.user) and instance.added_by != self.request.user:
            raise permissions.PermissionDenied("You can only delete point records that you added.")

        # Update the member's individual points if there's a member associated
        if instance.member:
            try:
                membership = HouseMembership.objects.get(user=instance.member, house=instance.house)
                membership.points -= instance.points
                membership.save()
            except HouseMembership.DoesNotExist:
                pass

        instance.delete()


class HouseMembershipViewSet(viewsets.ModelViewSet):
    queryset = HouseMembership.objects.all()
    serializer_class = HouseMembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsHouseLeaderOrReadOnly]
    lookup_field = 'user__user_id'
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        queryset = HouseMembership.objects.all()
        house = self.request.query_params.get('house', None)
        if house is not None:
            queryset = queryset.filter(house__name=house)
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user__user_id=user)
        return queryset

    def perform_create(self, serializer):
        # Check if the user is a house leader of the house they're trying to add a member to
        if not is_admin(self.request.user):
            try:
                house_name = self.request.data.get('house')
                membership = HouseMembership.objects.get(user=self.request.user, house__name=house_name)
                if not membership.is_house_leader:
                    raise permissions.PermissionDenied("You must be a house leader to add members to this house.")
            except HouseMembership.DoesNotExist:
                raise permissions.PermissionDenied("You must be a member of this house to add members to it.")

        serializer.save()

    def perform_destroy(self, instance):
        """Delete all point records associated with the member being removed from the house"""
        # Get the user and house from the membership instance
        user = instance.user
        house = instance.house

        # Delete all point records for this member in this house
        HousePointRecord.objects.filter(member=user, house=house).delete()

        # Now delete the membership
        instance.delete()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_house(request):
    """Get the house of the current user"""
    try:
        membership = HouseMembership.objects.get(user=request.user)
        return Response({
            'house': membership.house.name,
            'color': membership.house.color,
            'is_leader': membership.is_house_leader,
            'individual_points': membership.individual_points
        })
    except HouseMembership.DoesNotExist:
        return Response({'detail': 'User is not a member of any house'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_house_leaderboard(request):
    """Get the leaderboard of all houses"""
    houses = House.objects.all()
    leaderboard = []

    for house in houses:
        total_points = house.total_points
        member_count = HouseMembership.objects.filter(house=house).count()
        leaderboard.append({
            'name': house.name,
            'color': house.color,
            'total_points': total_points,
            'member_count': member_count
        })

    # Sort by total points in descending order
    leaderboard = sorted(leaderboard, key=lambda x: x['total_points'], reverse=True)

    return Response(leaderboard)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_house_members_leaderboard(request, house_name):
    """Get the leaderboard of members within a specific house"""
    house = get_object_or_404(House, name=house_name)
    memberships = HouseMembership.objects.filter(house=house)

    leaderboard = []
    for membership in memberships:
        leaderboard.append({
            'user_id': membership.user.user_id,
            'name': f"{membership.user.preferred_name} {membership.user.last_name}",
            'is_leader': membership.is_house_leader,
            'individual_points': membership.individual_points
        })

    # Sort by individual points in descending order
    leaderboard = sorted(leaderboard, key=lambda x: x['individual_points'], reverse=True)

    return Response(leaderboard)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_house_points_history(request, house_name):
    """Get the history of points for a specific house"""
    house = get_object_or_404(House, name=house_name)
    records = HousePointRecord.objects.filter(house=house).order_by('date_added')

    history = []
    cumulative_points = 0

    for record in records:
        cumulative_points += record.points
        member_name = f"{record.member.preferred_name} {record.member.last_name}" if record.member else "House"
        history.append({
            'id': record.id,
            'date': record.date_added,
            'points': record.points,
            'cumulative_points': cumulative_points,
            'description': record.description,
            'event': record.description or "Manual Entry",  # Use description as event name
            'member': {
                'id': record.member.user_id if record.member else None,
                'name': member_name
            },
            'added_by': {
                'id': record.added_by.user_id if record.added_by else None,
                'name': f"{record.added_by.preferred_name} {record.added_by.last_name}" if record.added_by else "System"
            }
        })

    return Response(history)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsHouseLeaderOfMember])
def add_member_points(request, user_id):
    """Add points to a member by a house leader"""
    # Get the member user
    member = get_object_or_404(CustomUser, user_id=user_id)

    # Validate the request data
    if 'points' not in request.data:
        return Response({'detail': 'Points field is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        points = float(request.data['points'])
        if points <= 0:
            return Response({'detail': 'Points must be positive'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'detail': 'Points must be a number'}, status=status.HTTP_400_BAD_REQUEST)

    description = request.data.get('description', 'Points added by house leader')

    # Get the house membership of the member
    try:
        member_membership = HouseMembership.objects.get(user=member)
        house = member_membership.house
    except HouseMembership.DoesNotExist:
        return Response({'detail': 'Member is not in any house'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a house point record for the house
    house_record = HousePointRecord.objects.create(
        house=house,
        points=points,
        description=description,
        added_by=request.user,
        member=member  # Add the member who earned the points
    )

    # Calculate the updated points total
    updated_points = member_membership.individual_points

    return Response({
        'detail': f'Added {points} points to {member.preferred_name} {member.last_name}',
        'house_record': HousePointRecordSerializer(house_record).data,
        'member_points': updated_points
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def edit_point_record(request, record_id):
    """Edit a point record"""
    record = get_object_or_404(HousePointRecord, id=record_id)

    # Check permissions
    if not is_admin(request.user) and record.added_by != request.user:
        return Response({'detail': 'You can only edit point records that you added.'},
                        status=status.HTTP_403_FORBIDDEN)

    # Validate the request data
    if 'points' not in request.data:
        return Response({'detail': 'Points field is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        points = float(request.data['points'])
        if points <= 0:
            return Response({'detail': 'Points must be positive'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'detail': 'Points must be a number'}, status=status.HTTP_400_BAD_REQUEST)

    description = request.data.get('description', record.description)

    # Update the record
    record.points = points
    record.description = description
    record.save()

    return Response({
        'detail': f'Updated point record for {record.house.name}',
        'house_record': HousePointRecordSerializer(record).data
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_point_record(request, record_id):
    """Delete a point record"""
    record = get_object_or_404(HousePointRecord, id=record_id)

    # Check permissions
    if not is_admin(request.user) and record.added_by != request.user:
        return Response({'detail': 'You can only delete point records that you added.'},
                        status=status.HTTP_403_FORBIDDEN)

    # Store information for the response
    house_name = record.house.name
    points = record.points

    # Delete the record
    record.delete()

    return Response({
        'detail': f'Deleted point record of {points} points from {house_name}'
    })