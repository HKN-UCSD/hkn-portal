from rest_framework.permissions import BasePermission


class HasDangerousEventPermissions(BasePermission):
    def has_permission(self, request, view):
        hpm = request.user.has_perm
        return (
            hpm("api.change_event") and hpm("api.add_event") and hpm("api.delete_event")
        )
