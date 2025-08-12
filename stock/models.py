from .constants import MaterialChoices, CategoryChoices, KaratChoices
from django.utils import timezone
from django.db import models
from datetime import date


class Stock(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_date = models.DateField()
    material = models.CharField(
        max_length=50,
        choices=MaterialChoices.choices(),
        default=MaterialChoices.OTHER.value
    )
    category = models.CharField(
        max_length=50,
        choices=CategoryChoices.choices(),
        default=CategoryChoices.OTHER.value
    )
    karat = models.CharField(
        max_length=5,
        choices=KaratChoices.choices(),
        default=KaratChoices.TWENTY_FOUR.value
    )
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.purchase_date:
            self.purchase_date = timezone.now().date()

        super().save(*args, **kwargs)
