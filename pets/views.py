from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from pets.models import Pet
from pets.serializers import PetSerializer, PetCreateUpdateSerializer


class PetCreateAPIView(APIView):
    """Создание питомца"""

    @extend_schema(
        summary='Создать питомца',
        request=PetCreateUpdateSerializer,
        responses={
            status.HTTP_201_CREATED: PetSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=None, description='Ошибка валидации'),
        },
    )
    def post(self, request):
        """Создать нового питомца"""
        serializer = PetCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        output_serializer = PetSerializer(serializer.instance)
        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)


class PetUpdateAPIView(APIView):
    """Обновление питомца"""

    @extend_schema(
        summary='Обновить питомца',
        request=PetCreateUpdateSerializer,
        responses={
            status.HTTP_200_OK: PetSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=None, description='Питомец не найден'),
        },
    )
    def put(self, request, pet_id):
        """Полностью обновить данных питомца"""

        pet = get_object_or_404(Pet.objects.prefetch_related('owner'), id=pet_id, owner=request.user)
        
        serializer = PetCreateUpdateSerializer(pet, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = PetSerializer(serializer.instance)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Частично обновить питомца',
        request=PetCreateUpdateSerializer,
        responses={
            status.HTTP_200_OK: PetSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=None, description='Питомец не найден'),
        },
    )
    def patch(self, request, pet_id):
        """Частично обновить данных питомца"""
        pet = get_object_or_404(Pet.objects.prefetch_related('owner'), id=pet_id, owner=request.user)
        
        serializer = PetCreateUpdateSerializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = PetSerializer(serializer.instance)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)


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
