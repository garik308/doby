import logging

from django.db.models import Q, Max
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from pets.models import Pet, PetPhoto
from pets.serializers import PetSerializer, PetUpdateSerializer, PetPhotoSerializer


class PetCreateAPIView(APIView):
    """Создание питомца"""

    parser_classes = [MultiPartParser]

    @extend_schema(
        summary='Создать питомца',
        request=PetSerializer,
        responses={
            status.HTTP_201_CREATED: PetSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=None, description='Ошибка валидации'),
        },
    )
    def post(self, request):
        """Создать нового питомца"""
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_photos = serializer.validated_data.pop('uploaded_photos', [])
        pet = serializer.save(owner=request.user)

        for idx, photo_file in enumerate(uploaded_photos, start=1):
            PetPhoto.objects.create(
                pet=pet,
                image=photo_file,
                order_number=idx + 1,
                is_main=(idx == 0),
            )

        return Response(
            data=PetSerializer(Pet.objects.prefetch_related('photos').get(id=pet.id)).data,
            status=status.HTTP_201_CREATED,
        )


class PetUpdateAPIView(APIView):
    """Обновление питомца"""

    parser_classes = [MultiPartParser]

    input_serializer = PetUpdateSerializer
    output_serializer = PetSerializer

    @extend_schema(
        summary='Обновить питомца',
        request=input_serializer,
        responses={
            status.HTTP_200_OK: output_serializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=None, description='Питомец не найден'),
        },
    )
    def put(self, request, pet_id):
        """Полностью обновить данных питомца"""

        pet = get_object_or_404(Pet.objects.prefetch_related('owner'), id=pet_id, owner=request.user)
        
        serializer = self.input_serializer(pet, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        uploaded_photos = serializer.validated_data.pop('uploaded_photos', [])
        photo_ids = serializer.validated_data.pop('photo_ids')
        serializer.save()
        PetPhoto.objects.filter(~Q(id__in=photo_ids) & Q(pet=pet)).delete()
        for idx, photo_file in enumerate(uploaded_photos, start=1):
            PetPhoto.objects.create(
                pet=pet,
                image=photo_file,
                order_number=idx + 1,
                is_main=(idx == 0),
            )

        return Response(
            data=self.output_serializer(Pet.objects.prefetch_related('photos').get(id=pet.id)).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary='Частично обновить питомца',
        request=input_serializer,
        responses={
            status.HTTP_200_OK: output_serializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=None, description='Питомец не найден'),
        },
    )
    def patch(self, request, pet_id):
        """Частично обновить данных питомца"""
        pet = get_object_or_404(Pet.objects.prefetch_related('owner'), id=pet_id, owner=request.user)
        serializer = self.input_serializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        uploaded_photos = serializer.validated_data.pop('uploaded_photos', [])
        photo_ids = serializer.validated_data.pop('photo_ids', None)
        serializer.save()
        if photo_ids is not None:
            PetPhoto.objects.filter(~Q(id__in=photo_ids) & Q(pet=pet)).delete()
        for idx, photo_file in enumerate(uploaded_photos, start=1):
            PetPhoto.objects.create(
                pet=pet,
                image=photo_file,
                order_number=idx + 1,
                is_main=(idx == 0),
            )

        return Response(
            data=self.output_serializer(Pet.objects.prefetch_related('photos').get(id=pet.id)).data,
            status=status.HTTP_201_CREATED,
        )


class PetRetrieveAPIView(APIView):
    """Получение данных питомца"""

    @extend_schema(
        summary='Получить данные питомца',
        responses={
            status.HTTP_200_OK: PetSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=None, description='Питомец не найден'),
        },
    )
    def get(self, request, user_uuid, pet_id):
        """Полностью обновить данных питомца"""
        pet = get_object_or_404(Pet.objects.prefetch_related('owner'), id=pet_id, owner__uuid=user_uuid)
        return Response(data=PetSerializer(pet).data, status=status.HTTP_200_OK)



class PetRetrieveAllAPIView(APIView):
    """Получение данные всех питомцев"""

    @extend_schema(
        summary='Получить данные всех питомцев',
        responses={
            status.HTTP_200_OK: PetSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=None, description='Пользователь не найден'),
        },
    )
    def get(self, request, user_uuid):
        """Получение данные всех питомцев"""
        pets = Pet.objects.prefetch_related('owner').filter(owner__uuid=user_uuid)
        return Response(data=PetSerializer(pets, many=True).data, status=status.HTTP_200_OK)


class PetPhotoCreateView(APIView):
    input_serializer = PetPhotoSerializer
    output_serializer = PetPhotoSerializer
    parser_classes = [MultiPartParser]

    # @квавава.jpg;type = image / jpeg
    @extend_schema(
        summary='Добавить фото питомцу',
        request=input_serializer,
        responses={
            status.HTTP_201_CREATED: input_serializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=None, description='Ошибка валидации'),
        },
    )
    def post(self, request, pet_id):
        """Загрузить новое фото для питомца (один файл)"""
        serializer = self.input_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        max_order = pet.photos.aggregate(Max('order_number'))['order_number__max'] or 0

        PetPhoto.objects.create(
            pet=pet,
            image=serializer.validated_data['image'],
            order_number=max_order + 1,
            is_main=False,
        )

        output_serializer = PetPhotoSerializer(pet.photos.all(), many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)