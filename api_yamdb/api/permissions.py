from rest_framework import permissions


class IsAuthorOrModeratorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (request.method in permissions.SAFE_METHODS
                or user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if (user.is_authenticated and (user.is_admin_role
                                       or user.is_moderator_role
                                       or obj.author == user)):
            return True
        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    message = 'Требуются права Администратора.'

    def has_permission(self, request, view):
        user = request.user
        if (user.is_authenticated
                and (user.is_admin_role or user.is_superuser)):
            return True


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Требуются права Администратора.'

    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        elif (user.is_authenticated
              and (user.is_admin_role or user.is_superuser)):
            return True
