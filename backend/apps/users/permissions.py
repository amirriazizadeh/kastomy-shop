from rest_framework.permissions import BasePermission


class IsSellerUser(BasePermission):
    message = "You must register as seller before performing this action"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_seller", False)
        )
