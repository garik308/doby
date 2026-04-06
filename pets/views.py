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

        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        
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
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        
        serializer = PetCreateUpdateSerializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = PetSerializer(serializer.instance)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)
