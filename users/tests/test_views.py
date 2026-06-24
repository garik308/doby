import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestUserUpdate:
    def test_update_user_success(self, auth_client, user_owner):
        url = reverse('me-update')  # предполагаем, что такой есть
        data = {'first_name': 'John', 'last_name': 'Doe'}
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        user_owner.refresh_from_db()
        assert user_owner.first_name == 'John'