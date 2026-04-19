from django.urls import path
from chats.views import ChatRoomDetailView, MessageMediaRetrieveView, MessageCreateView

urlpatterns = [
    path('<int:pk>/', ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('messages/', MessageCreateView.as_view(), name='chat_message_create'),
    path('messages/<int:message_id>/media/', MessageMediaRetrieveView.as_view(), name='chat_message_media_retrieve'),
]