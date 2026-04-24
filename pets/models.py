from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models

from pets.constants import PetType
from pets.storages import pet_photo_upload_path
from utils.file_type import IMAGE_EXTENSIONS
from utils.mixins import AutoDateMixin


class Pet(AutoDateMixin):
    """Model: Домашнее животное"""

    pet_type = models.CharField(
        verbose_name='Тип животного',
        max_length=20,
        choices=PetType.choices,
        default=PetType.DOG
    )
    owner = models.ForeignKey(
        'users.User',
        related_name='pets',
        verbose_name='Владелец',
        on_delete=models.SET_NULL,
        null=True,
    )
    name = models.CharField(verbose_name='Имя питомца', max_length=100)
    age = models.IntegerField(verbose_name='Возраст', validators=[MinValueValidator(1), MaxValueValidator(100)])
    height = models.IntegerField(verbose_name='Рост, см', validators=[MinValueValidator(1), MaxValueValidator(500)], null=True, blank=True)
    weight = models.IntegerField(verbose_name='Вес, кг', validators=[MinValueValidator(1), MaxValueValidator(300)], null=True, blank=True)
    breed_name = models.CharField(verbose_name='Название породы', max_length=100, blank=True, default='')
    diet_type = models.CharField(verbose_name='Тип питания', max_length=100, blank=True)
    diet_pattern = models.CharField(verbose_name='Режим питания', max_length=100, blank=True)
    diet_additional_info = models.CharField(verbose_name='Доп. Информация по питанию', max_length=200, blank=True)
    warning_tags = models.JSONField(verbose_name='Важные предупреждения', blank=True, default=list)
    specific_features = models.JSONField(verbose_name='Особенности', blank=True, default=list)

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'


class PetPhoto(AutoDateMixin):
    """Model: Фотографии питомцев"""

    pet = models.ForeignKey(verbose_name='Питомец', to='pets.Pet', related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(
        verbose_name='Фото',
        upload_to=pet_photo_upload_path,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'tiff', 'ico'])],
    )
    order_number = models.IntegerField(verbose_name='Порядок отображения',
                                       validators=[MinValueValidator(1), MaxValueValidator(100)])
    is_main = models.BooleanField(verbose_name='Основное фото', default=False)

    class Meta:
        verbose_name = 'Фото питомца'
        verbose_name_plural = 'Фото питомцев'
