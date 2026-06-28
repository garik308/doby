import json

import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from pets.models import Pet, PetPhoto
from tests.factories import UserFactory
from utils.test_utils import create_test_image
from .factories import PetFactory, PetPhotoFactory

pytestmark = pytest.mark.django_db


class TestPetCreate:
    def test_create_pet_without_photos(self, auth_client):
        url = reverse('pet-create')
        data = {
            'name': 'Rex',
            'pet_type': 'dog',
            'age': 3,
            'sex': 'male',
            'height': 50,
            'weight': 20,
            'breed_name': 'Labrador',
            'diet_type': 'dry',
            'diet_pattern': 'twice daily',
            'warning_tags': ['aggressive'],
            'specific_features': ['loves swimming'],
            'additional_info': 'friendly',
            'diet_additional_info': 'no bones',
        }
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert Pet.objects.count() == 1
        pet = Pet.objects.first()
        assert pet.name == 'Rex'
        assert pet.photos.count() == 0
        assert pet.warning_tags == ['aggressive']
        assert pet.specific_features == ['loves swimming']

    def test_create_pet_with_photos(self, auth_client):
        url_create = reverse('pet-create')
        data = {
            'name': 'Rex',
            'pet_type': 'dog',
            'age': 3,
            'sex': 'male',
            'height': 50,
            'weight': 20,
            'breed_name': 'Labrador',
            'diet_type': 'dry',
            'diet_pattern': 'twice daily',
            'warning_tags': ['aggressive'],
            'specific_features': ['loves swimming'],
            'additional_info': 'friendly',
            'diet_additional_info': 'no bones',
        }
        response = auth_client.post(url_create, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        pet_id = response.data['id']

        url_photo = reverse('pet-photos-create', args=[pet_id])
        image1 = create_test_image("photo1.jpg")
        image2 = create_test_image("photo2.jpg")

        response = auth_client.post(url_photo, {'image': image1, 'is_main': True, 'order_number': 1}, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        response = auth_client.post(url_photo, {'image': image2, 'is_main': True, 'order_number': 1}, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED

        pet = Pet.objects.get(id=pet_id)
        assert pet.photos.count() == 2
        assert pet.photos.filter(is_main=True).count() == 1

    def test_create_pet_invalid_data(self, auth_client):
        url = reverse('pet-create')
        data = {'name': ''}
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPetUpdateDelete:
    def test_update_pet_full(self, auth_client, pet):
        url = reverse('pet-update-delete', args=[pet.id])
        data = {
            'name': 'NewName',
            'pet_type': 'cat',
            'age': 5,
            'height': 40,
            'weight': 15,
            'breed_name': 'Persian',
            'warning_tags': ['calm'],
            'specific_features': ['sleepy'],
        }
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        pet.refresh_from_db()
        assert pet.name == 'NewName'
        assert pet.pet_type == 'cat'

    def test_update_pet_partial(self, auth_client, pet):
        url = reverse('pet-update-delete', args=[pet.id])
        data = {'name': 'NewName'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        pet.refresh_from_db()
        assert pet.name == 'NewName'

    def test_update_pet_with_photos_and_delete(self, auth_client, pet):
        photo1 = PetPhotoFactory(pet=pet, order_number=1, is_main=True)
        photo2 = PetPhotoFactory(pet=pet, order_number=2, is_main=False)
        url = reverse('pet-update-delete', args=[pet.id])
        new_image = create_test_image("new.jpg")
        data = {
            'name': 'Updated',
            'uploaded_photos': [new_image],
            'photo_ids': [photo1.id],
            'warning_tags': json.dumps(['calm']),
            'specific_features': json.dumps(['sleepy']),
        }
        response = auth_client.patch(url, data, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        pet.refresh_from_db()
        assert PetPhoto.objects.filter(pet=pet).count() == 2  # photo1 + новое
        assert PetPhoto.objects.filter(id=photo2.id).exists() is False
        new_photo = PetPhoto.objects.filter(pet=pet).exclude(id=photo1.id).first()
        assert new_photo is not None
        assert PetPhoto.objects.get(id=photo1.id).is_main is True

    def test_delete_pet(self, auth_client, pet):
        url = reverse('pet-update-delete', args=[pet.id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert Pet.objects.count() == 0

    def test_update_pet_not_found(self, auth_client):
        url = reverse('pet-update-delete', args=[999])
        response = auth_client.put(url, {'name': 'test'})
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPetRetrieve:
    def test_retrieve_pet(self, auth_client, user_owner, pet):
        url = reverse('user-pet-retrieve', args=[user_owner.uuid, pet.id])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == pet.id
        assert response.data['name'] == pet.name

    def test_retrieve_pet_not_found(self, auth_client, user_owner):
        url = reverse('user-pet-retrieve', args=[user_owner.uuid, 999])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPetRetrieveAll:
    def test_retrieve_all_pets(self, auth_client, user_owner):
        # создадим несколько питомцев для этого пользователя
        pet1 = PetFactory(owner=user_owner)
        pet2 = PetFactory(owner=user_owner)
        # создадим питомца другого пользователя (не должен появиться)
        other_user = UserFactory()
        PetFactory(owner=other_user)
        url = reverse('user-pet-retrieve-all', args=[user_owner.uuid])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        ids = [p['id'] for p in response.data]
        assert pet1.id in ids
        assert pet2.id in ids


class TestPetPhotoCreate:
    def test_add_photo(self, auth_client, pet):
        url = reverse('pet-photos-create', args=[pet.id])
        image = create_test_image('photo.jpg')
        data = {'image': image, 'is_main': False, 'order_number': 2}
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert PetPhoto.objects.filter(pet=pet).count() == 1
        assert 'id' in response.data

    def test_add_photo_make_main(self, auth_client, pet):
        # сначала создадим основное фото
        main_photo = PetPhotoFactory(pet=pet, is_main=True)
        url = reverse('pet-photos-create', args=[pet.id])
        image = create_test_image('photo.jpg')
        data = {'image': image, 'is_main': True, 'order_number': 2}
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        new_photo = PetPhoto.objects.get(id=response.data['id'])
        assert new_photo.is_main is True
        main_photo.refresh_from_db()
        assert main_photo.is_main is False

    def test_add_photo_pet_not_found(self, auth_client):
        url = reverse('pet-photos-create', args=[999])
        image = create_test_image('photo.jpg')
        data = {'image': image, 'is_main': True, 'order_number': 2}
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPetPhotoDelete:
    def test_delete_photo(self, auth_client, pet):
        photo = PetPhotoFactory(pet=pet)
        url = reverse('pet-photos-delete', args=[photo.id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert PetPhoto.objects.count() == 0

    def test_delete_photo_not_found(self, auth_client):
        url = reverse('pet-photos-delete', args=[999])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_photo_unauthorized(self, auth_client, pet):
        # создать фото для чужого питомца
        other_user = UserFactory()
        other_pet = PetFactory(owner=other_user)
        photo = PetPhotoFactory(pet=other_pet)
        url = reverse('pet-photos-delete', args=[photo.id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # т.к. фото не принадлежит текущему пользователю