from django.db import transaction
from django.db.models import Max
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking
from pets.models import Pet
from users.models import City, DeletedUser, UserPhoto
from users.serializers import CitySerializer, UserUpdateSerializer, UserRetieveSerializer, UserBaseSerializer, \
    UserForDeleteSerializer, UserPhotoSerializer


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


class DeleteUserProfileView(APIView):
    """Удаляет аккаунт пользователя"""

    @extend_schema(
        summary=__doc__,
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='Пользователь успешно удален'),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=None,
                                                          description='Учетные данные не были предоставлены'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(response=None,
                                                                   description='Ошибка на стороне сервера'),
        },
    )
    def post(self, request):
        """Удаляет аккаунт пользователя"""
        # TODO: сделать таской
        user = request.user
        deleted_user = DeletedUser(**UserForDeleteSerializer(user).data)
        with transaction.atomic():
            deleted_user.booking_ids_as_owner = [
                {'id': booking['id']}
                for booking in Booking.objects.filter(owner=user).values_list('id', flat=True)
            ]
            deleted_user.booking_ids_as_sitter = [
                {'id': booking['id']}
                for booking in Booking.objects.filter(sitter=user).values_list('id', flat=True)
            ]
            deleted_user.pet_ids = {
                {'id': pet['id']}
                for pet in Pet.objects.filter(owner=user).values_list('id', flat=True)
            }
            deleted_user.is_sitter = user.sitter_profile.exists()
            user.delete()
            deleted_user.save()

        return Response()


class UserPhotoCreateView(APIView):
    input_serializer = UserPhotoSerializer
    output_serializer = UserPhotoSerializer
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary='Добавить фото Пользователю',
        request=input_serializer,
        responses={
            status.HTTP_201_CREATED: output_serializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=None, description='Ошибка валидации'),
        },
    )
    def post(self, request):
        """Загрузить новое фото для питомца (один файл)"""
        serializer = self.input_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        max_order = request.user.photos.aggregate(Max('order_number'))['order_number__max'] or 0
        UserPhoto.objects.create(
            user=request.user,
            image=serializer.validated_data['image'],
            order_number=max_order + 1,
            is_main=False,
        )

        output_serializer = self.output_serializer(request.user.photos.all(), many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class UserPhotoDeleteView(APIView):
    output_serializer = UserPhotoSerializer
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary='Добавить фото Пользователю',
        request=None,
        responses={
            status.HTTP_201_CREATED: output_serializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=None, description='Ошибка валидации'),
        },
    )
    def delete(self, request, photo_id):
        """Удалить фото пользователя"""
        photo = get_object_or_404(UserPhoto, pk=photo_id)
        photo.delete()
        return Response(
            self.output_serializer(request.user.photos.all(), many=True).data,
            status=status.HTTP_201_CREATED,
        )
