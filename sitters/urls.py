from django.urls import path

from sitters.views import SittersPaginatedAPIView, SitterNearbyView

urlpatterns = [
    path('', SittersPaginatedAPIView.as_view(), name='paginated_sitters'),
    path('nearby/', SitterNearbyView.as_view(), name='sitters-nearby'),
]