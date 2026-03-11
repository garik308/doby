from django.urls import path

from users.views import UserRetrieveAPIView, CitiesRetrieveAPIView

urlpatterns = [
    path('me/', UserRetrieveAPIView.as_view(), name='me'),
    path('cities/', CitiesRetrieveAPIView.as_view(), name='cities'),
]