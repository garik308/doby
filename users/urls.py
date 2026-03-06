from django.urls import path

from users.views import UserRetrieveAPIView

urlpatterns = [
    path('me/', UserRetrieveAPIView.as_view(), name='me'),
]