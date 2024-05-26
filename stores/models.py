from django.db import models
from common.models import CommonModel
from django.conf import settings

class Store(CommonModel):

    class StoreMenuChoices(models.TextChoices):
        FOOD = ("음식", "음식")
        CAFE = ("카페", "카페")
        ECT = ("기타", "기탄")

    name = models.CharField(max_length=200, default="")
    description = models.TextField()
    kind_menu = models.CharField(max_length=20, choices=StoreMenuChoices)
    pet_friendly = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
     
    owner = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name="rooms",
        )
    
    sell_list = models.ManyToManyField(
    "stores.SellList",
    related_name="foods",
    )
    
    def __str__(self):
        return self.name


    def total_rate(store):
        count = store.reviews.count()
        if count == 0:
            return "No Ratings"
        else:
            total_rating = 0
            for review in store.reviews.all():
                if review.total_rating is not None:
                    total_rating += review.total_rating
            return round(total_rating / count, 1)
    
    def taste_rate(store):
        count = store.reviews.count()  # reviews = related_name
        if count == 0:
            return "No Ratings"
        else:
            total_rating = 0
            valid_ratings = 0
            for review in store.reviews.all():
                if review.taste_rating is not None:
                    total_rating += review.taste_rating
                    valid_ratings += 1
            if valid_ratings > 0:
                return round(total_rating / valid_ratings, 1)
            else:
                return "No Valid Ratings"
        
    def atmosphere_rate(store):
        count = store.reviews.count()  # reviews = related_name
        if count == 0:
            return "No Ratings"
        else:
            total_rating = 0
            valid_ratings = 0
            for review in store.reviews.all():
                if review.atmosphere_rating is not None:
                    total_rating += review.atmosphere_rating
                    valid_ratings += 1
            if valid_ratings > 0:
                return round(total_rating / valid_ratings, 1)
            else:
                return "No Valid Ratings"
        
    def kindness_rate(store):
        count = store.reviews.count()  # reviews = related_name
        if count == 0:
            return "No Ratings"
        else:
            total_rating = 0
            valid_ratings = 0
            for review in store.reviews.all():
                if review.kindness_rating is not None:
                    total_rating += review.kindness_rating
                    valid_ratings += 1
            if valid_ratings > 0:
                return round(total_rating / valid_ratings, 1)
            else:
                return "No Valid Ratings"
        
    def clean_rate(store):
        count = store.reviews.count()  # reviews = related_name
        if count == 0:
            return "No Ratings"
        else:
            total_rating = 0
            valid_ratings = 0
            for review in store.reviews.all():
                if review.clean_rating is not None:
                    total_rating += review.clean_rating
                    valid_ratings += 1
            if valid_ratings > 0:
                return round(total_rating / valid_ratings, 1)
            else:
                return "No Valid Ratings"
    
    def parking_rate(store):
        count = store.reviews.count()  # reviews = related_name
        if count == 0:
            return "No Ratings"
        else:
            total_rating = 0
            valid_ratings = 0
            for review in store.reviews.all():
                if review.parking_rating is not None:
                    total_rating += review.parking_rating
                    valid_ratings += 1
            if valid_ratings > 0:
                return round(total_rating / valid_ratings, 1)
            else:
                return "No Valid Ratings"
        
    def restroom_rate(store):
        count = store.reviews.count()  # reviews = related_name
        if count == 0:
            return "No Ratings"
        else:
            total_rating = 0
            valid_ratings = 0
            for review in store.reviews.all():
                if review.restroom_rating is not None:
                    total_rating += review.restroom_rating
                    valid_ratings += 1
            if valid_ratings > 0:
                return round(total_rating / valid_ratings, 1)
            else:
                return "No Valid Ratings"
        
    def reviews_len(store):
        count = store.reviews.count()
        if count == 0:
            return 0
        return count
        
    class Meta:
        verbose_name_plural = "Store"

class SellList(CommonModel):
    
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Selling List"