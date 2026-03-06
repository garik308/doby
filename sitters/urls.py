from django.urls import path

from sitters.views import SittersAPIView

urlpatterns = [
    path('', SittersAPIView.as_view(), name='paginated_sitters'),
]