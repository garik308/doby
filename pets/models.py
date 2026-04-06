from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from pets.constants import PetType
from utils.mixins import AutoDateMixin


class Pet(AutoDateMixin):
    """Model: Домашнее животное"""

    pet_type = models.CharField(
        verbose_name='Тип животного',
        max_length=20,
        choices=PetType.choices,
        default=PetType.DOG
    )
    name = models.CharField(verbose_name='Имя питомца', max_length=100)
    age = models.IntegerField(verbose_name='Возраст', validators=[MinValueValidator(1), MaxValueValidator(100)])
    owner = models.ForeignKey('users.User', verbose_name='Владелец', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'