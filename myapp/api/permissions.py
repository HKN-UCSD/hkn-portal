from rest_framework.permissions import BasePermission, SAFE_METHODS

def is_admin(user):
    """
    Helper function that returns whether the given user should have admin privileges
    """
    return user.is_superuser or user.groups.filter(name='officer').exists()

class HasAdminPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="officer").exists() or request.user.is_superuser

class IsStaffOrReadOnly(BasePermission):
    """
    Custom permission to only allow staff members to edit objects.
    Read-only permissions are allowed for any request.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to staff
        return is_admin(request.user)

class IsHouseLeaderOrReadOnly(BasePermission):
    """
    Custom permission to allow house leaders to edit their own house data.
    Read-only permissions are allowed for any request.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True

        # Check if user is admin
        if is_admin(request.user):
            return True

        # Check if user is a house leader
        from myapp.api.models.houses import HouseMembership
        try:
            membership = HouseMembership.objects.get(user=request.user)
            return membership.is_house_leader
        except HouseMembership.DoesNotExist:
            return False

class IsHouseLeaderOfMember(BasePermission):
    """
    Custom permission to allow house leaders to add points to members of their house.
    """
    def has_permission(self, request, view):
        # Check if user is admin
        if is_admin(request.user):
            return True

        # Check if user is a house leader
        from myapp.api.models.houses import HouseMembership
        try:
            membership = HouseMembership.objects.get(user=request.user)
            return membership.is_house_leader
        except HouseMembership.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Check if user is admin
        if is_admin(request.user):
            return True

        # Check if user is a house leader of the member's house
        from myapp.api.models.houses import HouseMembership
        try:
            leader_membership = HouseMembership.objects.get(user=request.user)
            member_membership = HouseMembership.objects.get(user=obj)
            return leader_membership.is_house_leader and leader_membership.house == member_membership.house
        except HouseMembership.DoesNotExist:
            return False
