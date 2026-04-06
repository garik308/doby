#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doby.settings')
django.setup()

from django.contrib.auth import get_user_model
from bookings.models import Booking
from pets.models import Pet
from pets.constants import PetType
from chats.models import ChatRoom
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Создаём пользователя
user, _ = User.objects.get_or_create(
    username='test_ws_user',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
user.set_password('testpass123')
user.save()

# Создаём ситтера
sitter, _ = User.objects.get_or_create(
    username='test_ws_sitter',
    defaults={
        'email': 'sitter@example.com',
        'first_name': 'Sitter',
        'last_name': 'User'
    }
)
sitter.set_password('testpass123')
sitter.save()

# Создаём питомца
pet, _ = Pet.objects.get_or_create(
    name='TestPet',
    defaults={
        'pet_type': PetType.DOG,
        'age': 3,
        'owner': user
    }
)

# Создаём букинг
booking, _ = Booking.objects.get_or_create(
    owner=user,
    sitter=sitter,
    pet=pet,
    defaults={
        'start_datetime': timezone.now() + timedelta(days=1),
        'end_datetime': timezone.now() + timedelta(days=2),
        'status': 'pending'
    }
)

# Создаём чат (сигнал должен создать автоматически, но на всякий случай)
chat, _ = ChatRoom.objects.get_or_create(
    booking=booking
)
chat.participants.add(user, sitter)

# Генерируем токен
token = AccessToken.for_user(user)

print("\n=== ДАННЫЕ ДЛЯ ТЕСТИРОВАНИЯ ===")
print(f"Username: {user.username}")
print(f"Password: testpass123")
print(f"Chat ID: {chat.id}")
print(f"Booking ID: {booking.id}")
print(f"JWT Token: {token}")
print(f"\nWebSocket URL:")
print(f"ws://localhost:8000/ws/chat/{chat.id}/?token={token}")
print("=" * 50)
