"""
Custom permissions for the API.
"""

from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to unauthenticated users,
    but require authentication for write operations.
    
    Note: In our case, we're using IsAuthenticated for all endpoints,
    so this is a placeholder if we need to relax permissions later.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always return True for read operations
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to authenticated users
        return request.user and request.user.is_authenticated
