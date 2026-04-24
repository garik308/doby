from rest_framework import serializers

from pets.serializers import PetSerializer
from users.models import City


class SitterProfileSerializer(serializers.Serializer):
    experience_years = serializers.IntegerField(allow_null=True, required=False)
    price_per_hour = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        allow_null=True,
        required=False
    )
    is_verified = serializers.BooleanField(read_only=True)


class CitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(label='Имя')
    translit = serializers.CharField(label='Транслит')


class UserBaseSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    username = serializers.CharField(label='Почта', max_length=150)
    first_name = serializers.CharField(label='Имя', max_length=255)
    last_name = serializers.CharField(label='Фамилия', max_length=255)
    patronymic = serializers.CharField(label='Отчество', max_length=255)
    phone = serializers.CharField(max_length=15)
    city = CitySerializer(label='Город')
    bio = serializers.CharField(max_length=500, allow_blank=True)


class UserRetieveSerializer(UserBaseSerializer):
    pets = PetSerializer(label='Питомцы', many=True)


class UserUpdateSerializer(serializers.Serializer):
    """Сериализатор обновления данных пользователя"""
    first_name = serializers.CharField(label='Имя', max_length=255, required=False)
    last_name = serializers.CharField(label='Фамилия', max_length=255, required=False)
    patronymic = serializers.CharField(label='Отчество', max_length=255, required=False)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        required=False,
        allow_null=True,
        label='Город'
    )
    bio = serializers.CharField(max_length=1500, required=False, allow_blank=True)


class UserForDeleteSerializer(UserBaseSerializer):
    user_id = serializers.IntegerField(read_only=True, source='user.id')
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        required=False,
        allow_null=True,
        label='Город',
    )
