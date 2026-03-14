from django.urls import path
from .views import ChatRoomDetailView

urlpatterns = [
    path('chat/<int:pk>/', ChatRoomDetailView.as_view(), name='chat-room-detail'),
]