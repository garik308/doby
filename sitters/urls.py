from django.urls import path

from sitters.views import SittersPaginatedAPIView

urlpatterns = [
    path('', SittersPaginatedAPIView.as_view(), name='paginated_sitters'),
]