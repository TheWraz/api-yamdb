from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
    )
    email = models.EmailField('Email', unique=True, max_length=254)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=20, choices=ROLE_CHOICES, default=USER
    )
    confirmation_code = models.CharField(
        'Код подтверждения', max_length=6, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""

        return self.is_superuser or self.role == self.ADMIN or self.is_staff
