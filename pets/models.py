from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from utils.mixins import AutoDateMixin


class Dog(AutoDateMixin):
    """Model: Собака"""

    name = models.CharField(verbose_name='Имя питомца', max_length=100)
    age = models.IntegerField(verbose_name='Возраст', validators=[MinValueValidator(1), MaxValueValidator(100)])
    owner = models.ForeignKey('users.User', verbose_name='Владелец', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Собака'
        verbose_name_plural = 'Собаки'