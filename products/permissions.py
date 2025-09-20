from rest_framework import permissions

class IsStaffUser(permissions.BasePermission):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


