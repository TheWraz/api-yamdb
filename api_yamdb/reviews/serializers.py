from rest_framework import serializers

from .models import Review, Comment


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.ReadOnlyField()
    # Поменять потом, пока просто отображаем ID

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.ReadOnlyField()
    # Поменять потом, пока просто отображаем ID
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'comments')
