from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, mixins, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from titles.models import Category, Genre, Title
from reviews.models import Review, Comment
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsModeratorOrAuthorOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer,
)


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet для категорий с возможностью создания, просмотра и удаления."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet для жанров с возможностью создания, просмотра и удаления."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений с поддержкой фильтров, поиска и рейтинга."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).select_related('category').prefetch_related('genre')
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Возвращает сериализатор для чтения или записи."""
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для обработки операций с отзывами. """

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = ReviewSerializer
    permission_classes = [IsModeratorOrAuthorOrReadOnly]

    def get_queryset(self):
        """Возвращает queryset отзывов для конкретного произведения."""
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)
# 1 Рано. Сперва нужно проверить что произведение вообще существует.
# Используем get_object_or_404.
# 2 Мы уже умеем пользоваться related_name. Используй его вместо filter чтобы получить все отзывы по производению.

    def create(self, request, *args, **kwargs):
# Лишний метод. Вся валидация происходит в сериализаторе. Вынеси проверку в validate.
        """Проверяем уникальность перед созданием."""
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)

        if Review.objects.filter(author=request.user, title=title).exists():
            return Response(
                {'error': 'Вы уже оставляли отзыв на это произведение'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Устанавливает автора и произведение при создании отзыва."""
        title_id = self.kwargs.get('title_id')
        title = Title.objects.get(id=title_id)
# 1 Рано. Сперва нужно проверить что произведение вообще существует.
# Используем get_object_or_404.
# Давай получение произведения вынесем в отдельный метод чтобы не повторяться.
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для обработки операций с комментариями."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = CommentSerializer
    permission_classes = [IsModeratorOrAuthorOrReadOnly]

    def get_queryset(self):
        """Возвращает queryset комментариев для конкретного отзыва."""
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)
# 1 Рано. Сперва нужно проверить что произведение вообще существует.
# Используем get_object_or_404.
# 2 Мы уже умеем пользоваться related_name. Используй его вместо filter чтобы получить все отзывы по производению.

    def perform_create(self, serializer):
        """Устанавливает автора и отзыв при создании комментария."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
# Давай получение отзыва вынесем в отдельный метод чтобы не повторяться.
        serializer.save(author=self.request.user, review=review)
