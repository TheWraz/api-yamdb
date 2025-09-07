from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from rest_framework import status, viewsets, mixins, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import IsAdmin
from .serializers import (
    SignupSerializer,
    TokenObtainSerializer,
    UserSerializer,
    MeSerializer,
)

User = get_user_model()


class UsersPagination(PageNumberPagination):
    """Пагинация для списка пользователей."""

    page_size = 10


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """Регистрация нового пользователя."""

    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    username = serializer.validated_data['username']

    user_by_username = User.objects.filter(username=username).first()
    user_by_email = User.objects.filter(email=email).first()

    if user_by_username and user_by_email:
        if user_by_username.id != user_by_email.id:
            return Response(
                {
                    'username':
                    ['Пользователь с таким username уже существует.'],
                    'email':
                    ['Пользователь с таким email уже существует.'],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user_by_username
    elif user_by_username:
        return Response(
            {'username': ['Пользователь с таким username уже существует.']},
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif user_by_email:
        return Response(
            {'email': ['Пользователь с таким email уже существует.']},
            status=status.HTTP_400_BAD_REQUEST,
        )
    else:
        user = User.objects.create(username=username, email=email)

    confirmation_code = '0'
    user.confirmation_code = confirmation_code
    user.save(update_fields=['confirmation_code'])

    send_mail(
        subject='YaMDb confirmation code',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=None,
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
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if (
        not user.confirmation_code
        or confirmation_code != user.confirmation_code
    ):
        return Response(
            {'confirmation_code': ['Неверный код подтверждения.']},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
