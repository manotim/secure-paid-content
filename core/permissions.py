from rest_framework.permissions import BasePermission

class IsMerchant(BasePermission):
    """
    Allows access only to users with the 'creator' role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "creator"
