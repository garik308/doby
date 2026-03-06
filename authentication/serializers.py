from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label='Почта', allow_blank=True)
    phone = serializers.CharField(label='Телефон', allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'phone', 'city')

class OutputRegisterSerializer(serializers.Serializer):
    user = UserSerializer(label='Данные о пользователе')
    access_token = serializers.CharField(label='Токен доступа')
    refresh_token = serializers.CharField(label='Токен для обновления access_token')