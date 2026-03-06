from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserSerializer


class UserRetrieveAPIView(APIView):
    """Получить Данные текущего пользователя"""

    output_serializer = UserSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=UserSerializer),
            # status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response={'message': 'Учетные данные не были предоставлены'}),
        },
    )
    def get(self, request):
        user = request.user
        serializer = self.output_serializer(instance=user)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.validated_data, status=status.HTTP_200_OK)