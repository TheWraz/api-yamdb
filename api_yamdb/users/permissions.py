from rest_framework.permissions import BasePermission
# Всё что касается АПИ - разрешения, серилизаторы, маршрутизаторы, вью размещаются в директории api.

class IsAdmin(BasePermission):
    """Разрешение для доступа только администраторам."""

    def has_permission(self, request, view):
        """Проверяет права доступа для запроса."""

        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
# Не повторяйся. Используй соответствующий метод в модели.
                or getattr(user, 'role', None) == 'admin'
                or user.is_staff
# Стафф это не суперюзер.
            )
        )
