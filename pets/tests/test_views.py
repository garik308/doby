import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from pets.models import Pet, PetPhoto
from tests.factories import UserFactory
from .factories import PetFactory, PetPhotoFactory

pytestmark = pytest.mark.django_db

class TestPetCreate:
    def test_create_pet_without_photos(self, auth_client):
        url = reverse('pet-create')
        data = {
            'name': 'Rex',
            'pet_type': 'dog',
            'age': 3,
            'height': 50,
            'weight': 20,
            'breed_name': 'Labrador'
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Pet.objects.count() == 1
        pet = Pet.objects.first()
        assert pet.name == 'Rex'
        assert pet.photos.count() == 0

    def test_create_pet_with_photos(self, auth_client):
        url = reverse('pet-create')
        image1 = SimpleUploadedFile("photo1.jpg", b"content", content_type="image/jpeg")
        image2 = SimpleUploadedFile("photo2.jpg", b"content", content_type="image/jpeg")
        data = {
            'name': 'Rex',
            'pet_type': 'dog',
            'age': 3,
            'uploaded_photos': [image1, image2]
        }
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        pet = Pet.objects.first()
        assert pet.photos.count() == 2
        # первое фото должно быть основным
        assert pet.photos.filter(is_main=True).count() == 1
        assert pet.photos.first().is_main is True

    def test_create_pet_invalid_data(self, auth_client):
        url = reverse('pet-create')
        data = {'name': ''}  # невалидные данные
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPetUpdateDelete:
    def test_update_pet_full(self, auth_client, pet):
        url = reverse('pet-detail', args=[pet.id])
        data = {
            'name': 'NewName',
            'pet_type': 'cat',
            'age': 5,
            'height': 40,
            'weight': 15,
            'breed_name': 'Persian'
        }
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        pet.refresh_from_db()
        assert pet.name == 'NewName'
        assert pet.pet_type == 'cat'

    def test_update_pet_partial(self, auth_client, pet):
        url = reverse('pet-detail', args=[pet.id])
        data = {'name': 'NewName'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        pet.refresh_from_db()
        assert pet.name == 'NewName'

    def test_update_pet_with_photos_and_delete(self, auth_client, pet):
        # создадим фото для питомца
        photo1 = PetPhotoFactory(pet=pet, order_number=1, is_main=True)
        photo2 = PetPhotoFactory(pet=pet, order_number=2, is_main=False)
        url = reverse('pet-detail', args=[pet.id])
        new_image = SimpleUploadedFile("new.jpg", b"content", content_type="image/jpeg")
        data = {
            'name': 'Updated',
            'uploaded_photos': [new_image],
            'photo_ids': [photo1.id]  # оставляем только photo1 и новое фото
        }
        response = auth_client.patch(url, data, format='multipart')
        assert response.status_code == status.HTTP_200_OK
        pet.refresh_from_db()
        # photo2 должно быть удалено
        assert PetPhoto.objects.filter(pet=pet).count() == 2  # photo1 + новое
        assert PetPhoto.objects.filter(id=photo2.id).exists() is False
        # новое фото добавлено
        new_photo = PetPhoto.objects.filter(pet=pet).exclude(id=photo1.id).first()
        assert new_photo is not None
        # photo1 должно остаться основным
        assert PetPhoto.objects.get(id=photo1.id).is_main is True

    def test_delete_pet(self, auth_client, pet):
        url = reverse('pet-detail', args=[pet.id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Pet.objects.count() == 0

    def test_update_pet_not_found(self, auth_client):
        url = reverse('pet-detail', args=[999])
        response = auth_client.put(url, {'name': 'test'})
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPetRetrieve:
    def test_retrieve_pet(self, auth_client, pet):
        url = reverse('pet-detail', args=[pet.id])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == pet.id
        assert response.data['name'] == pet.name

    def test_retrieve_pet_not_found(self, auth_client):
        url = reverse('pet-detail', args=[999])
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
        url = reverse('pets-all')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        ids = [p['id'] for p in response.data]
        assert pet1.id in ids
        assert pet2.id in ids


class TestPetPhotoCreate:
    def test_add_photo(self, auth_client, pet):
        url = reverse('pet-photos-create', args=[pet.id])
        image = SimpleUploadedFile("photo.jpg", b"content", content_type="image/jpeg")
        data = {'image': image}
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert PetPhoto.objects.filter(pet=pet).count() == 1
        assert 'id' in response.data

    def test_add_photo_make_main(self, auth_client, pet):
        # сначала создадим основное фото
        main_photo = PetPhotoFactory(pet=pet, is_main=True)
        url = reverse('pet-photos-create', args=[pet.id])
        image = SimpleUploadedFile("photo.jpg", b"content", content_type="image/jpeg")
        data = {'image': image, 'is_main': True}
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        new_photo = PetPhoto.objects.get(id=response.data['id'])
        assert new_photo.is_main is True
        # предыдущее основное должно стать не основным
        main_photo.refresh_from_db()
        assert main_photo.is_main is False

    def test_add_photo_pet_not_found(self, auth_client):
        url = reverse('pet-photos-create', args=[999])
        image = SimpleUploadedFile("photo.jpg", b"content", content_type="image/jpeg")
        data = {'image': image}
        response = auth_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPetPhotoDelete:
    def test_delete_photo(self, auth_client, pet):
        photo = PetPhotoFactory(pet=pet)
        url = reverse('pet-photos-delete', args=[photo.id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
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