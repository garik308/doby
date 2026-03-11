from django.db import models


class AutoDateMixin(models.Model):
    """Миксин с полями создания и обновления"""

    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True