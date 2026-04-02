from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import City
from users.serializers import UserSerializer, CitySerializer


class UserRetrieveAPIView(APIView):
    """Получить Данные текущего пользователя"""

    output_serializer = UserSerializer

    @extend_schema(
        summary=__doc__,
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=output_serializer),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=None, description='Учетные данные не были предоставлены'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(response=None, description='Ошибка на стороне сервера'),
        },
    )
    def get(self, request):
        """Получить данные текущего пользователя"""
        user = request.user
        serializer = self.output_serializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CitiesRetrieveAPIView(APIView):
    """Получить все доступные города"""
    permission_classes = ()

    output_serializer = CitySerializer

    @extend_schema(
        summary=__doc__,
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=output_serializer),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(response=None, description='Ошибка на стороне сервера'),
        },
    )
    def get(self, request):
        """Получить все доступные города"""
        return Response(data=self.output_serializer(instance=City.objects.all(), many=True).data)
