from rest_framework import serializers

from api_yamdb.constants import FORBIDDEN_USERNAMES


def me_forbidden_validator(value):
    """
    Валидатор, запрещающий использование запрещенных ников в качестве username.
    """
    if value.lower() in FORBIDDEN_USERNAMES:
        raise serializers.ValidationError(
            f'Использование "{value}" в качестве username запрещено.'
        )
    return value
