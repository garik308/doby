from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.serializers import RegisterSerializer, OutputRegisterSerializer
from users.models import User
from users.serializers import UserSerializer


class RegisterView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]
    input_serializer_class = RegisterSerializer
    output_serializer_class = OutputRegisterSerializer

    @extend_schema(
        request=RegisterSerializer,
        responses=OutputRegisterSerializer,
    )
    def post(self, request):
        serializer = self.input_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            city=validated_data['city'],
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_data = UserSerializer(user).data
        return Response(
            self.output_serializer_class({
                'user': user_data,
                'access_token': access_token,
                'refresh_token': refresh_token,
            }).data,
            status=status.HTTP_201_CREATED,
        )
