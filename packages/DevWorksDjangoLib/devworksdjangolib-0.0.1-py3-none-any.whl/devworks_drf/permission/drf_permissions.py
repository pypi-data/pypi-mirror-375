from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class UserCheck(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active


class TokenOrStaffUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True


class NoAccess(BasePermission):
    def has_permission(self, request, view):
        return False


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
