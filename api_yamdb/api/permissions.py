from rest_framework import permissions


class AuthorOrRead(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAdmin(permissions.BasePermission):
    message = 'Требуются права Администратора.'

    def has_permission(self, request, view):
        if request.user.id is None:
            return False
        return request.user.role == "admin" or request.user.is_superuser


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Требуются права Администратора.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.id is None:
            return False
        return request.user.role == "admin" or request.user.is_superuser
