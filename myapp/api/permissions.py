from rest_framework.permissions import BasePermission

class HasDangerousEventPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("api.modify_events") or request.user.is_superuser
