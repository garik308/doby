import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)
    translit = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class User(AbstractUser):
    """Model: Пользователь"""

    uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True)
    first_name = models.CharField('Имя', blank=True, max_length=255)
    last_name = models.CharField('Фамилия', blank=True, max_length=255)
    patronymic = models.CharField('Отчество', blank=True, max_length=255)
    phone = models.CharField('номер телефона', max_length=15, null=True, blank=True)
    avatar = models.ImageField('аватарка', upload_to='avatars/', null=True, blank=True)
    city = models.ForeignKey(to='users.City', on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField('Информация', max_length=1500, blank=True)
    sitter_profile = models.OneToOneField(
        to='sitters.SitterProfile',
        on_delete=models.SET_NULL,
        related_name='user',
        null=True,
    )

    def __str__(self):
        return self.full_name

    @property
    def full_name(self) -> str:
        return ' '.join([
            name_element for name_element in [self.first_name, self.last_name, self.patronymic] if name_element
        ])

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                'phone',
                condition=models.Q(phone__isnull=False),
                name='user_phone_unique_if_filled',
            ),
        ]
