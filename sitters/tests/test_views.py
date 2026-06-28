import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import SitterProfileFactory
from .factories import SitterServiceFactory

@pytest.mark.django_db
class TestSitterNearby:
    def test_search_nearby(self, auth_client):
        sitter_profile = SitterProfileFactory(location_lat=55.7558, location_lng=37.6173)
        url = reverse('sitters-nearby')
        data = {
            'lat': 55.7558,
            'lng': 37.6173,
            'radius_km': 10,
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['uuid'] == str(sitter_profile.uuid)

    def test_search_with_service_filter(self, auth_client):
        sitter_profile = SitterProfileFactory(location_lat=55.7558, location_lng=37.6173)
        SitterServiceFactory(sitter=sitter_profile, service_type='walking', is_active=True)
        url = reverse('sitters-nearby')
        data = {
            'lat': 55.7558,
            'lng': 37.6173,
            'service': 'walking',
            'radius_km': 10
        }
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_search_out_of_radius(self, auth_client):
        SitterProfileFactory(location_lat=55.0, location_lng=37.0)
        url = reverse('sitters-nearby')
        data = {
            'lat': 55.7558,
            'lng': 37.6173,
            'radius_km': 1
        }
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0