from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator

from api_yamdb.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME
from api.validators import me_forbidden_validator
from titles.models import Category, Genre, Title
from reviews.models import Review, Comment


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений с жанрами и категорией."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating',
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи произведений через slug жанра и категории."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверяет, что пользователь не оставлял отзыв на произведение."""
        if self.context['request'].method == 'POST':
            title = self.context['view'].get_title()
            user = self.context['request'].user
            if Review.objects.filter(author=user, title=title).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение'
                )
        return data


User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователей."""

    email = serializers.EmailField(
        required=True,
        max_length=MAX_LENGTH_EMAIL,
        validators=[MaxLengthValidator(MAX_LENGTH_EMAIL)]
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True,
        validators=[UnicodeUsernameValidator(), me_forbidden_validator]
    )

    def validate(self, data):
        """Валидация комбинации username и email."""

        email = data.get('email')
        username = data.get('username')

        if len(email) > MAX_LENGTH_EMAIL:
            raise serializers.ValidationError({
                'email': [
                    f'Email не может быть длиннее {MAX_LENGTH_EMAIL} символов.'
                ]
            })

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email != user_by_username:
            error_message = {}

            if user_by_email is not None:
                error_message['email'] = (
                    ['Пользователь с таким email уже существует.']
                )

            if user_by_username is not None:
                error_message['username'] = (
                    ['Пользователь с таким username уже существует.']
                )

            raise serializers.ValidationError(error_message)

        return data


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения JWT токена."""

    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
    confirmation_code = serializers.CharField(
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для CRUD операций с пользователями."""

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'role', 'email'
        )


class MeSerializer(UserSerializer):
    """Сериализатор для работы с собственным профилем пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
