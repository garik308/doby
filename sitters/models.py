import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Value, DecimalField, FloatField
from django.db.models.expressions import RawSQL
from django.db.models.functions import Radians, Cos, Sin, ACos

from bookings.constants import ServiceTypeChoices
from utils.mixins import AutoDateMixin

EARTH_RADIUS = 6371


class SitterProfileQuerySet(models.QuerySet):
    def get_nearby_sitters(self, lat, lng, radius_km=10):
        distance = RawSQL(
            """
            %s * ACOS(
                COS(RADIANS(%s)) * COS(RADIANS(location_lat)) * 
                COS(RADIANS(location_lng) - RADIANS(%s)) + 
                SIN(RADIANS(%s)) * SIN(RADIANS(location_lat))
            )
            """,
            [EARTH_RADIUS, lat, lng, lat],
            output_field=models.FloatField()
        )
        return self.annotate(distance=distance).filter(distance__lte=radius_km).order_by('distance')


class SitterProfile(AutoDateMixin):
    """Model: Ситтер

    Данные о пользователе, который готов посидеть с вашей собакой
    """

    uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, primary_key=True)
    user = models.OneToOneField(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='sitter_profile',
        null=True,
        blank=True,
    )
    experience_years = models.IntegerField(
        'Количество лет опыта',
        blank=True,
        default=0,
        validators=[MinValueValidator(0)],
    )
    price_per_hour = models.DecimalField(
        'Стоимость в час',
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_verified = models.BooleanField('Подтвержден', default=False)
    bio = models.CharField('Описание ситтера', blank=True, max_length=1500)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # средний рейтинг

    objects = SitterProfileQuerySet.as_manager()

    def __str__(self):
        return f"Sitter profile {self.uuid}"

    class Meta:
        verbose_name = 'Профиль ситтера'
        verbose_name_plural = 'Профили ситтеров'
        indexes = [models.Index(fields=['dt_updated'], name='sitter_profile_dt_updated_idx')]




class SitterService(AutoDateMixin):
    sitter = models.ForeignKey(SitterProfile, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=ServiceTypeChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # своя цена, если отличается от базовой
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Сервис ситтера {self.service_type_id}"

    class Meta:
        verbose_name = 'Сервисы ситтера'
        verbose_name_plural = 'Сервисы ситтеров'
