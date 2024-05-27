from django.db import models
from common.models import CommonModel


class Photo(CommonModel):
    file = models.URLField()
    store = models.ForeignKey(
        "stores.Store",
        null=True,
        blank=True,
        default="",
        on_delete=models.CASCADE,
        related_name="photos",
    )
    
    def __str__(self):
        return "Photo File"