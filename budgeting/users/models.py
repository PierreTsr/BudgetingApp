from django.db import models


class User(models.Model):
    firstName = models.CharField(
        max_length=32, blank=False, verbose_name="First name of an user."
    )
    lastName = models.CharField(
        max_length=32, blank=False, verbose_name="Last name of an user."
    )
