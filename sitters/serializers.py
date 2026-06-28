from django.db import models
from rest_framework import serializers

from bookings.constants import ServiceTypeChoices
from sitters.models import SitterProfile
from users.serializers import CitySerializer


class UserForSitterProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(label='Имя', max_length=255)
    last_name = serializers.CharField(label='Фамилия', max_length=255)
    patronymic = serializers.CharField(label='Отчество', max_length=255)
    avatar = serializers.ImageField(allow_null=True)
    city = CitySerializer(label='Город')
    bio = serializers.CharField(max_length=500, allow_blank=True)


class SitterSerialzer(serializers.Serializer):
    uuid = serializers.UUIDField(label='Идентификатор ситтера')
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


class SitterSearchInputSerializer(serializers.Serializer):
    lat = serializers.FloatField(help_text="Широта пользователя")
    lng = serializers.FloatField(help_text="Долгота пользователя")
    radius_km = serializers.FloatField(default=10, help_text="Радиус поиска в км")
    service = serializers.ChoiceField(
        choices=ServiceTypeChoices.choices,
        required=False,
        help_text="Тип услуги (boarding, walking, grooming, training)"
    )
    sort = serializers.ChoiceField(
        choices=['distance', 'rating', 'price'],
        default='distance',
        help_text="Поле для сортировки"
    )
    page = serializers.IntegerField(min_value=1, default=1)


class SitterListOutputSerializer(serializers.ModelSerializer):
    distance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_price = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SitterProfile
        fields = ('uuid', 'username', 'avatar', 'rating', 'distance', 'min_price', 'bio', 'location_lat', 'location_lng')

    def get_avatar(self, obj):
        avatar = obj.user.photos.first()
        return avatar.url if avatar else None

    def get_min_price(self, obj):
        min_price = obj.services.filter(is_active=True).aggregate(models.Min('price'))['price__min']
        return min_price