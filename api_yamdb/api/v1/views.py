from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, mixins, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from titles.models import Category, Genre, Title
from reviews.models import Review
from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsModeratorOrAuthorOrReadOnly,
    IsAdmin,
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer,
    SignupSerializer,
    TokenObtainSerializer,
    UserSerializer,
    MeSerializer,
)
from api.paginator import UsersPagination

User = get_user_model()


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

    def get_title(self):
        """Возвращает произведение по ID из URL."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        """Возвращает queryset отзывов для конкретного произведения."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Устанавливает автора и произведение при создании отзыва."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для обработки операций с комментариями."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = CommentSerializer
    permission_classes = [IsModeratorOrAuthorOrReadOnly]

    def get_review(self):
        """Возвращает отзыв по ID из URL."""
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        """Возвращает queryset комментариев для конкретного отзыва."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Устанавливает автора и отзыв при создании комментария."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """Регистрация нового пользователя."""

    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    username = serializer.validated_data['username']

    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )

    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        subject='YaMDb confirmation code',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
    return Response(
        {'email': email, 'username': username},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obtain_token(request):
    """Получение JWT токена для аутентификации."""

    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')

    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {'confirmation_code': ['Неверный код подтверждения.']},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD операции для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin)
    lookup_field = 'username'
    pagination_class = UsersPagination
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False, methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Работа с собственным профилем пользователя."""

        if request.method == 'GET':
            serializer = MeSerializer(request.user)
            return Response(serializer.data)
        serializer = MeSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
