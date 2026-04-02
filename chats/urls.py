from django.urls import path
from chats.views import ChatRoomDetailView

urlpatterns = [
    path('<int:pk>/', ChatRoomDetailView.as_view(), name='chat-room-detail'),
]