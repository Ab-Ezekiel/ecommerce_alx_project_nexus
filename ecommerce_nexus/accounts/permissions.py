from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow only staff users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """Allow customers to access only their own resources."""
    def has_object_permission(self, request, view, obj):
        # Admins can access anything
        if request.user.is_staff:
            return True

        # Customers can only access objects tied to them
        return obj.user == request.user
