from rest_framework import serializers


def me_forbidden_validator(value):
    """Валидатор, запрещающий использование 'me' в качестве username."""
    if value == 'me':
        raise serializers.ValidationError(
            'Использование "me" в качестве username запрещено.'
        )
    return value
