from django.urls import path

from users.views import MeRetrieveAPIView, MeUpdateAPIView, CitiesRetrieveAPIView

urlpatterns = [
    path('me/', MeRetrieveAPIView.as_view(), name='me'),
    path('me/update/', MeUpdateAPIView.as_view(), name='me-update'),
    path('cities/', CitiesRetrieveAPIView.as_view(), name='cities'),
]