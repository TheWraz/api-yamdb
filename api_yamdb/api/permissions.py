from rest_framework import permissions


class IsModeratorOrAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение модератору или автору."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.role == 'moderator'
            or request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение только админу."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user and request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdmin(permissions.BasePermission):
    """Разрешение для доступа только администраторам."""

    def has_permission(self, request, view):
        """Проверяет права доступа для запроса."""

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )
