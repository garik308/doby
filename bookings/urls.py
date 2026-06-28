from django.urls import path
from bookings.views import (
    BookingCreateView,
    BookingDetailView,
    UserBookingsListView,
    SitterBookingsListView,
    SitterBookingActionView, BookingCancelView,
)

urlpatterns = [
    path('', BookingCreateView.as_view(), name='booking-create'),
    path('me/', UserBookingsListView.as_view(), name='user-bookings'),
    path('me/<int:booking_id>/cancel/', BookingCancelView.as_view(), name='user-booking-cancel'),
    path('sitter/', SitterBookingsListView.as_view(), name='sitter-bookings'),
    path('<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:booking_id>/actions/', SitterBookingActionView.as_view(), name='booking-actions'),
]