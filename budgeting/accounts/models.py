from currencies.models import Currency
from django.db import models
from users.models import User


class Account(models.Model):
    user = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name="Owner of the account.",
    )
    currency = models.ForeignKey(
        Currency,
        models.PROTECT,
        verbose_name="Currency of the account.",
        blank=True,
    )
    name = models.CharField(
        max_length=128,
        verbose_name="Name of the account.",
    )


class Transaction(models.Model):
    account = models.ForeignKey(
        Account,
        models.CASCADE,
        verbose_name="The account on which this transaction was operated.",
    )
    category = models.ForeignKey(
        "categories.Category",
        models.RESTRICT,
    )
    name = models.CharField(max_length=256)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
