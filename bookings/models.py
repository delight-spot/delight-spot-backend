from django.db import models
from common.models import CommonModel
from django.conf import settings


class Booking(CommonModel):
    """Booking Model Definition"""
    name = models.CharField(
        max_length=150,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    store = models.ManyToManyField(
        "stores.Store",
        blank=True,
        default="",
        related_name="bookings",
    )

    def __str__(self):
        return self.name
