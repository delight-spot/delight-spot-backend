from django.contrib import admin
from .models import Reviews
from django.db.models import Avg
from django.db import models

@admin.register(Reviews)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",  # models.py 에서 설정한 str 메서드를 보여준다.
        "total_rating",
        "taste_rating",
        "atmosphere_rating",
        "kindness_rating",
        "clean_rating",
        "parking_rating",
        "restroom_rating",
        "store",
    )
    search_fields = (
        "store",
    )
    