from rest_framework import permissions


class IsAuthorOrModeratorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS or user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if not user.is_authenticated:
            return False
        if user.is_admin_role or user.is_moderator_role or obj.author == user:
            return True


class IsAdmin(permissions.BasePermission):
    message = 'Требуются права Администратора.'

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return user.is_admin_role or user.is_superuser


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
        