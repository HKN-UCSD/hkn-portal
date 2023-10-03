from rest_framework.permissions import BasePermission

def is_admin(user):
    """
    Helper function that returns whether the given user should have admin privileges
    """
    return user.is_superuser or user.groups.filter(name='officer').exists()

class HasAdminPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="officer").exists() or request.user.is_superuser
