from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import City
from users.serializers import CitySerializer, UserUpdateSerializer, UserRetieveSerializer


class MeRetrieveAPIView(APIView):
    """Получить Данные текущего пользователя"""

    output_serializer = UserRetieveSerializer

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
        serializer = self.output_serializer(instance=request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class MeUpdateAPIView(APIView):
    """Обновление данных текущего пользователя"""

    output_serializer = UserRetieveSerializer

    @extend_schema(
        summary='Обновить данные пользователя',
        request=UserUpdateSerializer,
        responses={
            status.HTTP_200_OK: output_serializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=None, description='Ошибка валидации'),
        },
    )
    def patch(self, request):
        """Частично обновить данные текущего пользователя"""
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=self.output_serializer(instance=request.user).data, status=status.HTTP_200_OK)


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
