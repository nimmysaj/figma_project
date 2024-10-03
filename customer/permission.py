from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow the owner of an account or admin to access/edit.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the customer or an admin
        return request.user == obj.user or request.user.is_staff or request.user.is_superuser
