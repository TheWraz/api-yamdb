from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from rest_framework import serializers


User = get_user_model()


class UsernameValidationMixin:
# Лишнее.
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
# Величины ограничений берем из констант.
# Тут и далее.
    username = serializers.CharField(max_length=150, required=True)
# Нужно указать все требуемые ограничения - длину строк и валидаторы (атрибут validators).
#-- Для валидации символов есть готовый валидатор UnicodeUsernameValidator() из django.contrib.auth.validators.
#-- Нужно добавить валидацию для ника me
# Для этого пишем кастомный валидатор.
# Оба этих валидатора пригодятся нам и в сериализаторе и в моделе.

#Валидацию для комбинации ника и почты описываем в методе validate.
#Подсказка:
#<пользователь-по-email> = User.objects...filter(<фильтр-по-почте>).first()
#<пользователь-по-username> = User.objects...filter(<фильтр-по-нику>).first()
#if <ранее-полученные-пользователи-не-равны>: 

    # если пользователи не равны значит что: 
    # либо ник занят, либо занята почта, либо и то и другое но разными пользователями
    # все что внутри этого условия это 400 код

#    error_msg = {} # сюда будем добавлять данные с отсутствующими полями

    # делаем дополнительные проверки чтобы выяснить в каком формате отдавать сообщение

    # если пользователь полученный выше (например, по почте) не None, значит поле с email занято 
    # эту информацию добавляем в error_msg (аналогично проверяем другое поле)

    # после всех проверок отдаем словарь (который уже учитывает все отсутствующие поля) 
    # по ожидаемой схеме и 400 код
class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения JWT токена."""

    username = serializers.CharField(required=True)
# Ограничения точно такие же как и выше.
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(UsernameValidationMixin, serializers.ModelSerializer):
    """Сериализатор для CRUD операций с пользователями."""
# Так как это модельный сериализатор, то все настройки полей (включая валидацию) 
# он подтянет из модели автоматически. Описывать поля нет необходимости если мы ничего не меняем.
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
# Лишнее.
            'first_name': {'max_length': 150, 'required': False},
            'last_name': {'max_length': 150, 'required': False},
            'username': {'max_length': 150},
            'email': {'max_length': 254},
        }


class MeSerializer(UserSerializer):
    """Сериализатор для работы с собственным профилем пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
