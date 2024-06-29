from django.db import models
from common.models import CommonModel
from django.conf import settings


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
    

class ReviewsPhoto(CommonModel):
    file = models.URLField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default="",
        on_delete=models.CASCADE,
        related_name="reviews_user",
    )

    reviews = models.ForeignKey(
        "reviews.Reviews",
        null=True,
        blank=True,
        default="",
        on_delete=models.SET_NULL,
        related_name="review_photos",
    )
    
    def __str__(self):
        return "Photo File"