from rest_framework.permissions import BasePermission

class IsFranchiseUser(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and if the user has a franchise role
        return request.user and request.user.is_authenticated and request.user.role == 'franchise'  # Adjust the field 'role' based on your User model
