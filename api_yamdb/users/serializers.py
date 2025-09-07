from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from rest_framework import serializers


User = get_user_model()


class UsernameValidationMixin:
    """Миксин для валидации username."""

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использование "me" в качестве username запрещено.'
            )
        username_validator = RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Допустимы только буквы, цифры и символы . @ + - _'
        )
        try:
            username_validator(value)
        except Exception:
            raise serializers.ValidationError(
                'Допустимы только буквы, цифры и символы . @ + - _'
            )
        return value


class SignupSerializer(UsernameValidationMixin, serializers.Serializer):
    """Сериализатор для регистрации пользователей."""

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения JWT токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(UsernameValidationMixin, serializers.ModelSerializer):
    """Сериализатор для CRUD операций с пользователями."""

    first_name = serializers.CharField(
        max_length=150, allow_blank=True, default='', required=False
    )
    last_name = serializers.CharField(
        max_length=150, allow_blank=True, default='', required=False
    )
    bio = serializers.CharField(allow_blank=True, default='', required=False)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'role', 'email'
        )
        extra_kwargs = {
            'first_name': {'max_length': 150, 'required': False},
            'last_name': {'max_length': 150, 'required': False},
            'username': {'max_length': 150},
            'email': {'max_length': 254},
        }


class MeSerializer(UserSerializer):
    """Сериализатор для работы с собственным профилем пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
