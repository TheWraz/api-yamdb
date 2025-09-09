from rest_framework import serializers

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
# Для рейтинга нужен IntegerField, в котором надо будет указать параметр default (дефолтом будет None).

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


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
# Некорректный формат ответа.
# Внимание на жанры, категорию и рейтинг.
# АПИ пишут в строгом соответствии с документацией, в противном случае твои коллеги на фронте могут не досчитаться данных. 
# Именно это сейчас происходит с полями категорий и жанров. Фронт ждет в поле категорий словарь, а мы отдаем ему строку, и т.д.
# Посмотри в сторону to_representation.
    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'comments')
# Не все поля нужны согласно ТЗ. Сверяемся со спецификацией.
