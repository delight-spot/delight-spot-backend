from django.db import models
from common.models import CommonModel
from django.conf import settings
from django.core.validators import MaxValueValidator


class Reviews(CommonModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    store = models.ForeignKey(
        "stores.Store",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviews",
    )
    
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    description = models.TextField()

    def __str__(self):
        return f"{self.user}: {self.rating}⭐️"