from rest_framework.permissions import BasePermission

class IsFranchiseAdminOrOwner(BasePermission):
    """
    Custom permission to allow only franchise admins or owners to add a service.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Modify the condition based on actual user role implementation
        return request.user.is_staff or request.user.groups.filter(name='FranchiseAdmin').exists()
