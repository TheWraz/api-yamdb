from rest_framework import viewsets, permissions

from .models import Review, Comment
from .serializers import ReviewSerializer, CommentSerializer
#  from .permissions import IsAuthorOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обработки операций с отзывами.
    Поддерживает все CRUD операции: создание, чтение, обновление, удаление.
    """
    serializer_class = ReviewSerializer
    # Пока разрешаем всё аутентифицированным пользователям.
    # После заменю на свой permission
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Возвращает queryset отзывов для конкретного произведения."""
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        """Устанавливает автора и произведение при создании отзыва."""
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user.id, title_id=title_id)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обработки операций с комментариями.
    Поддерживает все CRUD операции для комментариев к отзывам.
    """
    serializer_class = CommentSerializer
    # Пока разрешаем всё аутентифицированным пользователям.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Возвращает queryset комментариев для конкретного отзыва."""
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        """Устанавливает автора и отзыв при создании комментария."""
        review_id = self.kwargs.get('review_id')
        serializer.save(author=self.request.user.id, review_id=review_id)
