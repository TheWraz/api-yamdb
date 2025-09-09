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
# Конструкцию нужно вынести в одну строку, и с помощью оператора or объединить оба условия.
# return ... or ... 
# В случае если первое условие будет истинным следующей проверки не последует и вернется True.
        return (
            obj.author == request.user
# Проверку требующую запрос в БД лучше размещать в самом конце, для того, чтобы если остальные проверки не дали False лишний запрос в БД бы не совершался.
            or request.user.role == request.user.MODERATOR
# Проверку роли юзера стоит вынести в методы модели юзера и учесть в ней соотвествии роли и админа is_superuser.
# Соответственно, в разрешениях достаточно объявлять нужную проверку (например, .is_admin() или .is_moderator() чтобы проверить наличие роли).
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
