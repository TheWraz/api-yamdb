from django.contrib.auth.models import AbstractUser
from django.db import models

# ordering также должно быть в каждой модели
# строковое представление __str__
class CustomUser(AbstractUser):
# Не используем в названиях слова Custom или My. Они подходят только для учебных примеров, но не для реального кода.
    """Кастомная модель пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
# Используем TextChoice.
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
# Величины ограничений берем из констант. Тут и далее.
        unique=True,
    )
    email = models.EmailField('Email', unique=True, max_length=254)
# Это значение(254) по-умолчанию установлено в models.EmailField.
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=20, choices=ROLE_CHOICES, default=USER
    )
    confirmation_code = models.CharField(
# Код в БД хранить не надо.
        'Код подтверждения', max_length=6, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""

        return self.is_superuser or self.role == self.ADMIN or self.is_staff
# Стафф это не админ.
