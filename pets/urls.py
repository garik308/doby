from django.urls import path

from pets.views import (
    PetCreateAPIView,
    PetUpdateDeleteAPIView,
    PetRetrieveAPIView,
    PetRetrieveAllAPIView,
    PetPhotoCreateView,
    PetPhotoDeleteView,
)

urlpatterns = [
    path('', PetCreateAPIView.as_view(), name='pet-create'),
    path('<int:pet_id>/', PetUpdateDeleteAPIView.as_view(), name='pet-update-delete'),
    path('<int:pet_id>/photos/', PetPhotoCreateView.as_view(), name='pet-photos-create'),
    path('photos/<int:photo_id>/', PetPhotoDeleteView.as_view(), name='pet-photos-delete'),
    path('<uuid:user_uuid>/all/', PetRetrieveAllAPIView.as_view(), name='user-pet-retrieve-all'),
    path('<uuid:user_uuid>/<int:pet_id>/', PetRetrieveAPIView.as_view(), name='user-pet-retrieve'),
]
