import uuid

from django.core.validators import MinValueValidator
from django.db import models

from utils.mixins import AutoDateMixin


class SitterProfile(AutoDateMixin):
    """Model: Ситтер

    Данные о пользователе, который готов посидеть с вашей собакой
    """

    uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, primary_key=True)
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

    def __str__(self):
        return f"Sitter profile {self.id}"

    class Meta:
        verbose_name = 'Профиль ситтера'
        verbose_name_plural = 'Профили ситтеров'
        indexes = [models.Index(fields=['dt_updated'], name='sitter_profile_dt_updated_idx')]
