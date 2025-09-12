from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api_yamdb.constants import (
    MAX_LENGTH_USERNAME,
    MAX_LENGTH_ROLE,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
)

from api.v1.validators import me_forbidden_validator


class User(AbstractUser):
    """Кастомная модель пользователя."""

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator(), me_forbidden_validator],
    )
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField(
        'Имя', max_length=MAX_LENGTH_FIRST_NAME, blank=True,
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_LENGTH_LAST_NAME, blank=True
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=MAX_LENGTH_ROLE,
        choices=Role.choices,
        default=Role.USER,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.email})'

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""

        return self.role == self.Role.MODERATOR

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""

        return self.is_superuser or self.role == self.Role.ADMIN
