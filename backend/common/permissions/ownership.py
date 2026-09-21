"""Object-level permissions enforcing ownership and multi-tenant data isolation."""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to read or edit it.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Support user directly or objects with user/portfolio relationship
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "portfolio"):
            return obj.portfolio.user == request.user

        return False


class IsPortfolioOwner(permissions.BasePermission):
    """
    Permission specifically checking if the user owns the portfolio referenced in URL kwargs or body.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "portfolio"):
            return obj.portfolio.user == request.user
        return False
