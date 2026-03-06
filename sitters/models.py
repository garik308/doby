from django.db import models


class SitterProfile(models.Model):
    """Model: Ситтер

    Данные о пользователе, который готов посидеть с вашей собакой
    """

    experience_years = models.IntegerField('', null=True, blank=True)
    price_per_hour = models.DecimalField(
        'Стоимость в час',
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_verified = models.BooleanField('Подтвержден', default=False)

    def __str__(self):
        return f"Sitter profile for user {self.user_id}"
