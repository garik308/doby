from django.urls import path

from users.views import UserRetrieveAPIView, UserUpdateAPIView, CitiesRetrieveAPIView

urlpatterns = [
    path('me/', UserRetrieveAPIView.as_view(), name='me'),
    path('me/update/', UserUpdateAPIView.as_view(), name='me-update'),
    path('cities/', CitiesRetrieveAPIView.as_view(), name='cities'),
]