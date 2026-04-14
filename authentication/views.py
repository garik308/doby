from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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


# Вдруг понадобится
# class RegisterSitterAPIView(APIView):
#     """Зарегистрировать юзера как ситтера"""
#
#     authentication_classes = []
#     permission_classes = (AllowAny,)
#     input_serializer_class = ComplexSitterRegisterSerializer
#     output_serializer_class = OutputSitterRegisterSerializer
#
#     @extend_schema(
#         request=input_serializer_class,
#         responses={status.HTTP_201_CREATED: output_serializer_class,},
#     )
#     def post(self, request):
#         serializer = self.input_serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user_validated_data = serializer.validated_data['user_data']
#         sitter_validated_data = serializer.validated_data['sitter_data']
#         city_translit = user_validated_data.pop('city_translit')
#         email = user_validated_data.pop('email')
#         phone = user_validated_data.pop('phone')
#         if email and User.objects.filter(email__isnull=False, email=email).exists():
#             raise ValidationError({'detail': 'Email already registered'})
#         if phone and User.objects.filter(phone__isnull=False, phone=phone).exists():
#             raise ValidationError({'detail': 'Phone already registered'})
#
#         with transaction.atomic():
#             sitter = SitterProfile.objects.create(**sitter_validated_data)
#             city = City.objects.get(translit=city_translit)
#             user = User.objects.create_user(
#                 email=email,
#                 phone=phone,
#                 city=city,
#                 sitter=sitter,
#                 **user_validated_data,
#             )
#
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#         refresh_token = str(refresh)
#
#         user_data = UserSerializer(user).data
#         sitter_data = SitterSerialzer(sitter).data
#         return Response(
#             self.output_serializer_class({
#                 'user': user_data,
#                 'sitter': sitter_data,
#                 'access_token': access_token,
#                 'refresh_token': refresh_token,
#             }).data,
#             status=status.HTTP_201_CREATED,
#         )