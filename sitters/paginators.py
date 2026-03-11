from rest_framework.pagination import CursorPagination


class SittersPagination(CursorPagination):
    page_size = 1
    ordering = '-dt_updated'
    cursor_query_param = 'cursor'

