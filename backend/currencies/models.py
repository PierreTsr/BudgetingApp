from django.core.validators import MinLengthValidator
from django.db import models


class Currency(models.Model):
    identifier = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name="3 characters identifier of a currency",
        validators=[MinLengthValidator(3)],
    )
    symbol = models.CharField(
        max_length=1,
        verbose_name="Visual representation of the currency",
    )
