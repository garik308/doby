from rest_framework import serializers

from users.serializers import CitySerializer


class UserForSitterProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(label='Имя', max_length=255)
    last_name = serializers.CharField(label='Фамилия', max_length=255)
    patronymic = serializers.CharField(label='Отчество', max_length=255)
    avatar = serializers.ImageField(allow_null=True)
    city = CitySerializer(label='Город')
    bio = serializers.CharField(max_length=500, allow_blank=True)


class SittersPaginatedSerialzer(serializers.Serializer):
    id = serializers.IntegerField(label='Идентификатор ситтера')
    avatar = serializers.ImageField(allow_null=True)
    experience_years = serializers.IntegerField(label='Количество лет опыта')
    price_per_hour = serializers.DecimalField(
        label='Стоимость в час',
        max_digits=6,
        decimal_places=2,
        allow_null=True,
    )
    is_verified = serializers.BooleanField(label='Подтвержден')
    bio = serializers.CharField(label='Описание ситтера', max_length=1500)
    user = UserForSitterProfileSerializer(label='данные пользователя')