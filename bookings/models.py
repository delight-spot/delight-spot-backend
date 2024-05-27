from django.db import models
from common.models import CommonModel
from django.conf import settings


class Booking(CommonModel):
    """Booking Model Definition"""

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
        return f"{self.user}: {self.store}"
