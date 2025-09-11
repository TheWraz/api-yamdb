from rest_framework.pagination import PageNumberPagination

from api_yamdb.constants import PAGE_SIZE


class UsersPagination(PageNumberPagination):
    """Пагинация для списка пользователей."""

    page_size = PAGE_SIZE
