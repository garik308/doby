from rest_framework.views import APIView

from sitters.paginators import SittersPagination
from sitters.models import SitterProfile
from sitters.serializers import SittersPaginatedSerialzer


class SittersPaginatedAPIView(APIView):
    """Возвра"""

    input_serializer_class = SittersPaginatedSerialzer

    def get(self, request):
        """Получить данные ситтеров с пагинацией"""
        queryset = SitterProfile.objects.select_related('user')
        paginator = SittersPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.input_serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
