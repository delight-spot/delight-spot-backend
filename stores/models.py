from django.db import models
from common.models import CommonModel
from django.conf import settings

class Store(CommonModel):

    class StoreMenuChoices(models.TextChoices):
        FOOD = ("음식", "음식")
        COFFEE = ("카페", "카페")
    class StoreKindChoices(models.TextChoices):
        KO = (
            "한식",
            "한식",
        )
        JA = (
            "일식",
            "일식",
        )       
        CH = (
            "중식",
            "중식",
        )
        WF = (
            "양식",
            "양식",
        )
        OTHER = (
            "기타",
            "기타",
        )

    name = models.CharField(max_length=200, default="")
    description = models.TextField()
    kind_menu = models.CharField(max_length=20, choices=StoreMenuChoices)
    kind_detail = models.CharField(max_length=20, choices=StoreKindChoices)
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

    def rating(store):
        count = store.reviews.count()  # reviews = related_name
        if count == 0:
            return "No Reviews"
        else:
            total_rating = 0
            for review in store.reviews.all().values("rating"):
                total_rating += review.get("rating")
            return round(total_rating / count, 1)
        
    def reviews_len(store):
        count = store.reviews.count()
        if count == 0:
            return "No Reviews"
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