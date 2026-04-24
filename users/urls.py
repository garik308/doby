from django.urls import path

from users.views import (
    MeRetrieveAPIView,
    MeUpdateAPIView,
    CitiesRetrieveAPIView,
    DeleteUserProfileView,
    UserPhotoCreateView, UserPhotoDeleteView,
)

urlpatterns = [
    path('me/', MeRetrieveAPIView.as_view(), name='me'),
    path('me/update/', MeUpdateAPIView.as_view(), name='me-update'),
    path('cities/', CitiesRetrieveAPIView.as_view(), name='cities'),
    path('me/delete/', DeleteUserProfileView.as_view(), name='delete-user'),
    path('me/photos/', UserPhotoCreateView.as_view(), name='photos-create'),
    path('me/photos/<int:photo_id>/', UserPhotoDeleteView.as_view(), name='user-photo-delete'),
]