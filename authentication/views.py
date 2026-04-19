from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.serializers import (
    UserRegisterSerializer,
    OutputUserRegisterSerializer,
    OutputUserLoginSerializer,
)
from users.models import User


class RegisterView(APIView):
    """Зарегистрировать пользователя"""

    authentication_classes = ()
    permission_classes = (AllowAny,)
    input_serializer_class = UserRegisterSerializer
    output_serializer_class = OutputUserRegisterSerializer

    @extend_schema(
        request=UserRegisterSerializer,
        responses=OutputUserRegisterSerializer,
    )
    def post(self, request):
        serializer = self.input_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            raise ValidationError('Пользователь с такой почтой уже существует.')

        user = User.objects.create_user(**serializer.validated_data)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            self.output_serializer_class({
                'user': user,
                'access_token': access_token,
                'refresh_token': refresh_token,
            }).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):

    permission_classes = (AllowAny,)
    input_serializer_class = TokenObtainPairSerializer
    output_serializer_class = OutputUserLoginSerializer

    @extend_schema(
        request=input_serializer_class,
        responses=output_serializer_class,
    )
    def post(self, request):
        serializer = self.input_serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        return Response(
            OutputUserLoginSerializer({
                'user': serializer.user,
                'access_token': serializer.validated_data['access'],
                'refresh_token': serializer.validated_data['refresh'],
            }).data,
        )


class LogoutView(APIView):
    """Добавляет все пользовательские refresh-токены в черный список"""

    def post(self, request):
        already_revoked_count = 0
        tokens = OutstandingToken.objects.filter(user=request.user)
        for token in tokens:
            try:
                refresh_token = RefreshToken(token.token)
                refresh_token.blacklist()
            except Exception:
                # Токен, возможно, уже в черном списке или истек
                already_revoked_count += 1
                pass

        return Response({'revoke_count': len(tokens) - already_revoked_count}, status=status.HTTP_200_OK)
