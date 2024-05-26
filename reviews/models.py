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

    taste_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)], null=True, blank=True)
    atmosphere_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)], null=True, blank=True)
    kindness_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)], null=True, blank=True)
    clean_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)], null=True, blank=True)
    parking_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)], null=True, blank=True)
    restroom_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)], null=True, blank=True)

    description = models.TextField()

    @property
    def total_rating(self):
        ratings = [
            self.taste_rating,
            self.atmosphere_rating,
            self.kindness_rating,
            self.clean_rating,
            self.parking_rating,
            self.restroom_rating,
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        else:
            return None 

    def __str__(self):
        if self.total_rating is not None:
            return f"{self.total_rating:.1f}"
        else:
            return f"평점 리뷰가 없습니다"

        
        
    # total_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])

    # def __str__(self):
        # return f"{self.user}: {self.total_rating}⭐️"