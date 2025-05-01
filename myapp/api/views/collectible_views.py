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

from myapp.api.permissions import is_admin


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
    Logic:
    1. 30% chance of draft success
    2. Find rarities where user has unowned collectibles (avoid duplicates)
    3. Calculate weighted probabilities for rarities based on available ones
    4. Select a random collectible from the chosen rarity
    """
    user = request.user
    
    # Get available drafts
    draft_record = calculate_available_drafts(user)
    
    # Check if user has drafts available
    if draft_record.available_drafts <= 0:
        return Response({
            'error': 'No drafts available'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Step 1: Determine if draft is successful (30% chance)
    if random.random() > 0.3:
        return Response({
            'status': 'failure',
            'message': 'Draft attempt failed. Try again!'
        })
    
    # Step 2: Find rarities where user has unowned collectibles
    # Get all collectibles
    all_collectibles = CollectibleItem.objects.all()
    
    # Get user's owned collectibles
    user_collectibles = UserCollectible.objects.filter(user=user).values_list('item_id', flat=True)
    
    # Filter to only unowned collectibles
    unowned_collectibles = all_collectibles.exclude(id__in=user_collectibles)
    
    # If user owns all collectibles, return a message
    if not unowned_collectibles.exists():
        return Response({
            'status': 'failure',
            'message': 'You already own all available collectibles!'
        })
    
    # Count available collectibles by rarity
    rarity_counts = {}
    for rarity, _ in CollectibleItem.RARITY_CHOICES:
        count = unowned_collectibles.filter(rarity=rarity).count()
        if count > 0:
            rarity_counts[rarity] = count
    
    # Define base probabilities
    base_probabilities = {
        'common': 60,
        'rare': 25,
        'epic': 10,
        'legendary': 5
    }
    
    # Step 3: Calculate weighted probabilities based on available rarities
    available_rarities = list(rarity_counts.keys())
    weighted_probabilities = {}
    
    total_probability = 0
    for rarity in available_rarities:
        if rarity in base_probabilities:
            total_probability += base_probabilities[rarity]
    
    for rarity in available_rarities:
        if rarity in base_probabilities:
            weighted_probabilities[rarity] = base_probabilities[rarity] / total_probability
    
    # Select a rarity based on weighted probabilities
    rarity_roll = random.random()
    cumulative_prob = 0
    selected_rarity = available_rarities[0]  # Default to first available
    
    for rarity, prob in weighted_probabilities.items():
        cumulative_prob += prob
        if rarity_roll <= cumulative_prob:
            selected_rarity = rarity
            break
    
    # Step 4: Select a random collectible from the chosen rarity
    available_items = unowned_collectibles.filter(rarity=selected_rarity)
    selected_item = random.choice(available_items)
    
    # Add the collectible to user's collection
    UserCollectible.objects.create(
        user=user,
        item=selected_item,
        acquired_date=timezone.now()
    )
    
    # Update the draft token count
    draft_record.drafts_used += 1
    draft_record.available_drafts = max(0, draft_record.available_drafts - 1)
    draft_record.save()
    
    # Return the collectible info
    return Response({
        'status': 'success',
        'id': selected_item.id,
        'name': selected_item.name,
        'description': selected_item.description,
        'image_url': selected_item.image_url,
        'rarity': selected_item.rarity,
        'type': selected_item.type
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_loadout_data(request):
    """
    API endpoint to get user's loadout and inventory data.
    Returns equipped items by slot and all available collectibles.
    """
    user = request.user
    
    try:
        # Get all user collectibles
        user_collectibles = UserCollectible.objects.filter(user=user)
        
        # Prepare equipped items structure
        equipped = {
            'icon': None,
            'frame': None,
            'banner': None,
            'badge': None,
            'theme': None
        }
        
        # Get equipped items
        equipped_items = user_collectibles.filter(is_equipped=True)
        
        for item in equipped_items:
            item_slot = item.equipped_slot
            if item_slot in equipped:
                # Get full collectible item details
                collectible = item.item
                equipped[item_slot] = {
                    'id': collectible.id,
                    'name': collectible.name,
                    'description': collectible.description,
                    'image_url': collectible.image_url,
                    'rarity': collectible.rarity,
                    'type': collectible.type,
                    'is_equipped': True
                }
        
        # Get all available items (the user's inventory)
        available = []
        for user_item in user_collectibles:
            collectible = user_item.item
            available.append({
                'id': collectible.id,
                'name': collectible.name,
                'description': collectible.description,
                'image_url': collectible.image_url,
                'rarity': collectible.rarity,
                'type': collectible.type,
                'is_equipped': user_item.is_equipped
            })
        
        return Response({
            'equipped': equipped,
            'available': available
        })
    except Exception as e:
        return Response(
            {'error': f'Error fetching loadout data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def equip_collectible(request, collectible_id):
    """
    API endpoint to equip or unequip a collectible item.
    POST parameters:
        - slot: The slot to equip the item to (icon, frame, banner, badge, theme)
        - equip: Boolean indicating whether to equip (true) or unequip (false)
    """
    user = request.user
    
    try:
        # Parse request data
        slot = request.data.get('slot')
        equip = request.data.get('equip', False)
        
        # Get the user collectible
        user_collectible = get_object_or_404(
            UserCollectible, 
            user=user, 
            item_id=collectible_id
        )
        
        if equip and not slot:
            return Response(
                {'error': 'Slot must be specified when equipping an item'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # First, unequip any item currently in the specified slot
        if equip and slot:
            UserCollectible.objects.filter(
                user=user,
                is_equipped=True,
                equipped_slot=slot
            ).update(is_equipped=False, equipped_slot=None)
        
        # Then, equip or unequip the specified item
        user_collectible.is_equipped = equip
        user_collectible.equipped_slot = slot if equip else None
        user_collectible.save()
        
        return Response({
            'success': True,
            'message': f'Item {"equipped" if equip else "unequipped"} successfully',
            'item_id': collectible_id,
            'slot': slot,
            'equipped': equip
        })
    except Exception as e:
        return Response(
            {'error': f'Error equipping item: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_collectible(request):
    """
    API endpoint to add a new collectible to the database.
    Only accessible to admin users.
    """
    user = request.user
    
    # Check if user is an admin using the is_admin helper function
    if not is_admin(user):
        return Response(
            {'error': 'Only admin users can add new collectibles'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Validate required fields
        required_fields = ['name', 'image_url', 'type']
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create the new collectible
        serializer = CollectibleItemSerializer(data=request.data)
        if serializer.is_valid():
            collectible = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Collectible created successfully',
                'collectible': CollectibleItemSerializer(collectible).data
            })
        else:
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': f'Error creating collectible: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_collectible(request, collectible_id):
    """
    API endpoint to delete a collectible from the database.
    Only accessible to admin users.
    """
    user = request.user
    
    # Check if user is an admin
    if not is_admin(user):
        return Response(
            {'error': 'Only admin users can delete collectibles'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Find the collectible
        collectible = get_object_or_404(CollectibleItem, id=collectible_id)
        
        # Check if there are any user collectibles associated with this item
        user_collectibles_count = UserCollectible.objects.filter(item=collectible).count()
        if user_collectibles_count > 0:
            return Response(
                {
                    'error': 'This collectible cannot be deleted because it is owned by users',
                    'user_count': user_collectibles_count
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Store collectible info for the response
        collectible_name = collectible.name
        
        # Delete the collectible
        collectible.delete()
        
        return Response({
            'success': True,
            'message': f'Collectible "{collectible_name}" deleted successfully'
        })
    except Exception as e:
        return Response(
            {'error': f'Error deleting collectible: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 