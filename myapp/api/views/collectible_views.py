from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count
import random
import json

from myapp.api.models import (
    CustomUser, EventActionRecord, CollectibleItem, UserCollectible, DraftRecord
)

from myapp.api.serializers import (
    CollectibleItemSerializer, UserCollectibleSerializer, DraftRecordSerializer
)


class CollectibleViewSet(viewsets.ModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserCollectibleViewSet(viewsets.ModelViewSet):
    queryset = UserCollectible.objects.all()
    serializer_class = UserCollectibleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return UserCollectible.objects.filter(user=user)


class DraftRecordViewSet(viewsets.ModelViewSet):
    queryset = DraftRecord.objects.all()
    serializer_class = DraftRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return DraftRecord.objects.filter(user=user)


# Helper function to calculate available drafts based on attendance
def calculate_available_drafts(user):
    # Get all checked-off events for the user
    check_offs = EventActionRecord.objects.filter(
        acted_on=user,
        action="Check Off"
    ).exclude(points=0)
    
    # Every 3 events = 1 draft token
    events_attended = check_offs.count()
    
    # Get or create the user's draft record
    draft_record, created = DraftRecord.objects.get_or_create(user=user)
    
    # Calculate potential drafts from attendance (every 3 events = 1 draft)
    potential_drafts = events_attended // 3
    
    # If we got a higher number, update the record
    if potential_drafts > draft_record.available_drafts:
        draft_record.available_drafts = potential_drafts
        draft_record.last_calculated = timezone.now()
        draft_record.save()
    
    return draft_record


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_collectibles_home_data(request):
    """
    API endpoint for the collectibles home page.
    Returns available drafts, events attended, and featured/recent collectibles.
    """
    user = request.user
    
    # Calculate available drafts
    draft_record = calculate_available_drafts(user)
    
    # Get events attended count
    events_attended = EventActionRecord.objects.filter(
        acted_on=user,
        action="Check Off"
    ).exclude(points=0).count()
    
    # Get user's collectibles (recent)
    user_collectibles = UserCollectible.objects.filter(user=user).order_by('-acquired_date')[:5]
    recent_collectibles = [
        {
            'id': uc.item.id,
            'name': uc.item.name,
            'image_url': uc.item.image_url,
            'rarity': uc.item.rarity,
            'type': uc.item.type
        } for uc in user_collectibles
    ]
    
    # Featured collectibles (just select random ones for now)
    featured_ids = list(CollectibleItem.objects.values_list('id', flat=True))
    if len(featured_ids) > 3:
        featured_ids = random.sample(featured_ids, 3)
    
    featured_collectibles = [
        {
            'id': item.id,
            'name': item.name,
            'image_url': item.image_url,
            'rarity': item.rarity,
            'type': item.type,
            'description': item.description
        } for item in CollectibleItem.objects.filter(id__in=featured_ids)
    ]
    
    return Response({
        'events_attended': events_attended,
        'available_drafts': draft_record.available_drafts,
        'recent': recent_collectibles,
        'featured': featured_collectibles
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_drafts_data(request):
    """
    API endpoint to get drafts data.
    Returns available drafts and recent drafts.
    """
    user = request.user
    
    # Calculate available drafts
    draft_record = calculate_available_drafts(user)
    
    # Get user's recent collectibles (simulate drafts history)
    user_collectibles = UserCollectible.objects.filter(user=user).order_by('-acquired_date')[:5]
    recent_drafts = [
        {
            'id': uc.item.id,
            'name': uc.item.name,
            'image_url': uc.item.image_url,
            'rarity': uc.item.rarity
        } for uc in user_collectibles
    ]
    
    return Response({
        'available_drafts': draft_record.available_drafts,
        'recent_drafts': recent_drafts
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def perform_draft(request):
    """
    API endpoint to perform a draft.
    This is a dummy implementation that always 'fails' (doesn't consume draft tokens)
    but still returns a simulated collectible.
    """
    user = request.user
    
    # Get available drafts
    draft_record = calculate_available_drafts(user)
    
    # Check if user has drafts available (but don't actually use them)
    if draft_record.available_drafts <= 0:
        return Response({
            'error': 'No drafts available'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Simulate draft result based on rarity probabilities without consuming drafts
    rarity_roll = random.randint(1, 100)
    if rarity_roll <= 5:
        rarity = 'legendary'
    elif rarity_roll <= 15:
        rarity = 'epic'
    elif rarity_roll <= 40:
        rarity = 'rare'
    else:
        rarity = 'common'
    
    # Try to find an item of the selected rarity
    items = CollectibleItem.objects.filter(rarity=rarity)
    if not items.exists():
        # Fallback to any item
        items = CollectibleItem.objects.all()
    
    if not items.exists():
        # Create a placeholder item if no items exist
        placeholder = {
            'id': 0,
            'name': f'{rarity.capitalize()} Circuit Design',
            'image_url': f'/static/placeholder_{rarity}.png',
            'rarity': rarity
        }
        return Response(placeholder)
    
    # Select a random item
    item = random.choice(items)
    
    # Return the item without adding it to the user's collection or consuming a draft
    return Response({
        'id': item.id,
        'name': item.name,
        'image_url': item.image_url,
        'rarity': item.rarity
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_catalog_data(request):
    """
    API endpoint to get the full catalog of collectibles.
    Returns all collectible items for the catalog page.
    """
    try:
        items = CollectibleItem.objects.all().order_by('name')
        
        # Serialize the items
        serialized_items = []
        for item in items:
            serialized_items.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'image_url': item.image_url,
                'rarity': item.rarity,
                'type': item.type,
                'is_seasonal': item.is_seasonal
            })
        
        return Response(serialized_items)
    except Exception as e:
        return Response(
            {'error': f'Error fetching catalog data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 