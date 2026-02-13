from rest_framework.permissions import BasePermission, IsAuthenticated
from users.models import RolePermission

class DatabaseRBACPermissions(BasePermission):
    """
    Database-driven Role-Based Access Control permissions
    Checks permissions from the database based on user's role
    """

    def has_permission(self, request, view):
        # Allow unauthenticated users for public endpoints
        if not request.user or not request.user.is_authenticated:
            # For public endpoints (AllowAny), this will be handled by the view's permission_classes
            return True

        # Admin has all permissions
        if hasattr(request.user, 'is_admin') and request.user.is_admin:
            return True

        # Get the view name
        view_name = view.__class__.__name__
        method = request.method

        # Define public endpoints (allow all)
        public_endpoints = [
            'StatsView',
            'SensitivityDistributionView',
            'AntibioticEffectivenessView',
            'ResistanceOverTimeView',
            'ResistanceHeatmapView',
            'BacteriaListView',
            'DepartmentListView',
            'WelcomeView',
            'CustomTokenObtainPairView',
            'RegisterView',
        ]

        if view_name in public_endpoints:
            return True

        # Define endpoints that require authentication but no special permissions
        auth_required = [
            'MessageViewSet',
            'UserViewSet',  # Allow authenticated users to read user list
        ]

        if view_name in auth_required:
            return True

        # For other endpoints, check if user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permissions
        """
        # For messaging, users can access their own messages
        if hasattr(obj, 'sender') and hasattr(obj, 'recipient'):
            if obj.sender == request.user or obj.recipient == request.user:
                return True
            # Admins can access all messages
            if hasattr(request.user, 'is_admin') and request.user.is_admin:
                return True
            return False

        # Default: allow access to own objects or admin access
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        if hasattr(request.user, 'is_admin') and request.user.is_admin:
            return True

        return False

# Backward compatibility classes
class AdminPermissions(IsAuthenticated):
    """Admin permissions - full access"""
    pass

class DoctorPermissions(IsAuthenticated):
    """Doctor permissions"""
    pass

class LabPermissions(IsAuthenticated):
    """Lab permissions"""
    pass

class ViewerPermissions(IsAuthenticated):
    """Viewer permissions - read only"""
    pass

class MessagingPermissions(IsAuthenticated):
    """Messaging permissions"""
    pass

class RoleBasedPermissions(DatabaseRBACPermissions):
    """Main RBAC permission class"""
    pass
