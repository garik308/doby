from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from sitters.paginators import SittersPaginator
from sitters.models import SitterProfile
from sitters.serializers import SitterSerialzer


class SittersPaginatedAPIView(APIView):
    """Возвра"""

    serializer_class = SitterSerialzer

    @extend_schema(
        request=serializer_class,
    )
    def get(self, request):
        """Получить данные ситтеров с пагинацией"""

        queryset = SitterProfile.objects.select_related('user')
        paginator = SittersPaginator()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
