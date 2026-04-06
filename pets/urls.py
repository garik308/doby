from django.urls import path

from pets.views import PetCreateAPIView, PetUpdateAPIView

urlpatterns = [
    path('', PetCreateAPIView.as_view(), name='pet-create'),
    path('<int:pet_id>/', PetUpdateAPIView.as_view(), name='pet-update'),
]
