from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from sitters.paginators import SittersPaginator
from sitters.models import SitterProfile
from sitters.serializers import SitterSerialzer, SitterSearchInputSerializer, SitterListOutputSerializer


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


class SitterNearbyView(APIView):

    PAGE_SIZE = 30

    @extend_schema(
        summary="Поиск ближайших ситтеров",
        description="Возвращает список ситтеров в заданном радиусе с возможностью фильтрации по услуге и сортировки по расстоянию, рейтингу или цене.",
        request=SitterSearchInputSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=SitterListOutputSerializer(many=True), description="Успешный ответ"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Ошибка валидации"),
        }
    )
    def post(self, request):
        input_serializer = SitterSearchInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        qs = SitterProfile.objects.filter(
            location_lat__isnull=False,
            location_lng__isnull=False,
            user__is_active=True
        )

        if data.get('service'):
            qs = qs.filter(services__service_type=data['service'], services__is_active=True)

        qs = qs.get_nearby_sitters(data['lat'], data['lng'], radius_km=(data['radius_km']))

        sort_type = data['sort']
        if sort_type == 'rating':
            qs = qs.order_by('-rating')
        elif sort_type == 'price':
            qs = qs.annotate(min_price=models.Min('services__price')).order_by('min_price')

        offset = (data['page'] - 1) * self.PAGE_SIZE
        total = qs.count()
        results = qs[offset:offset + self.PAGE_SIZE]

        # 8. Сериализация ответа
        output_serializer = SitterListOutputSerializer(results, many=True)
        return Response(
            {
                'count': total,
                'page': (data['page']),
                'page_size': self.PAGE_SIZE,
                'results': output_serializer.data
            },
            status=status.HTTP_200_OK,
        )
