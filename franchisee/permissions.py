from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow owners or admins to edit a profile.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can access any profile
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Owners can access their own profile
        return obj.user == request.user  # Assuming `user` is a field in `ServiceProvider` linking to the `User` model


from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Custom permission to only allow owners to edit their own profile.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if the user is the owner
        return obj.user == request.user