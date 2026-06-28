import pytest
from django.urls import reverse
from django.core import mail
from rest_framework import status
from bookings.models import Booking
from bookings.constants import BookingStatus
from .factories import BookingFactory

pytestmark = [pytest.mark.django_db]

class TestBookingCreate:
    def test_create_success(self, auth_client, user_sitter, pet):
        url = reverse('booking-create')
        data = {
            'sitter_uuid': user_sitter.sitter_profile.uuid,
            'pet_id': pet.id,
            'service': 'walking',
            'start_datetime': '2025-06-01T10:00:00Z',
            'end_datetime': '2025-06-01T11:00:00Z',
            'comment': 'test'
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Booking.objects.count() == 1
        assert len(mail.outbox) == 1

    def test_create_overlapping(self, auth_client, user_sitter, pet):
        booking = BookingFactory(sitter=user_sitter.sitter_profile, pet=pet)
        url = reverse('booking-create')
        data = {
            'sitter_uuid': user_sitter.sitter_profile.uuid,
            'pet_id': pet.id,
            'service': 'walking',
            'start_datetime': booking.start_datetime.isoformat(),
            'end_datetime': booking.end_datetime.isoformat(),
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "{'error': 'Ситтер занят в это время, попробуйте другое'}" in str(response.data)


class TestBookingLists:
    def test_user_bookings(self, auth_client, user_owner):
        booking = BookingFactory(owner=user_owner)
        url = reverse('user-bookings')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_sitter_bookings(self, sitter_auth_client, user_sitter):
        booking = BookingFactory(sitter=user_sitter.sitter_profile)
        url = reverse('sitter-bookings')
        response = sitter_auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


class TestBookingActions:
    def test_accept_booking(self, sitter_auth_client, user_sitter):
        booking = BookingFactory(sitter=user_sitter.sitter_profile)
        url = reverse('booking-actions', args=[booking.id])
        data = {'action': 'accept'}
        response = sitter_auth_client.post(url, data)
        booking.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert booking.status == BookingStatus.CONFIRMED
        assert len(mail.outbox) == 1

    def test_cancel_booking(self, auth_client, user_owner):
        booking = BookingFactory(owner=user_owner)
        url = reverse('user-booking-cancel', args=[booking.id])
        data = {'action': 'cancel'}
        response = auth_client.post(url, data)
        booking.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert booking.status == BookingStatus.CANCELLED_BY_OWNER
