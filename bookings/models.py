from django.db import models
from common.models import CommonModel
from django.conf import settings


class Booking(CommonModel):
    """Booking Model Definition"""
    # class BookingKindChoices(models.TextChoices):
    #     FOOD_STORE = ("food_store", "음식점",)
    #     COFFEE_STORE = (
    #         "cafe",
    #         "카페",
        # )
    name = models.CharField(
        max_length=150,
    )
    
    # kind = models.CharField(
    #     max_length=15,
    #     choices=BookingKindChoices.choices,
    # )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    store = models.ManyToManyField(
        "stores.Store",
        null=True,
        blank=True,
        default="",
        related_name="bookings",
    )

    def __str__(self):
        return self.name
