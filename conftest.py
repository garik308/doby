import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from tests.factories import UserFactory, SitterProfileFactory, PetFactory


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_owner():
    return UserFactory()


@pytest.fixture
def user_sitter():
    user = UserFactory()
    SitterProfileFactory(user=user)
    return user


@pytest.fixture
def pet(user_owner):
    return PetFactory(owner=user_owner)

@pytest.fixture
def auth_client(api_client, user_owner):
    token = str(AccessToken.for_user(user_owner))
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

@pytest.fixture
def sitter_auth_client(api_client, user_sitter):
    token = str(AccessToken.for_user(user_sitter))
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client