from django.contrib import admin
from .models import Photo, ReviewsPhoto


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        "store",
    )

@admin.register(ReviewsPhoto)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        "reviews",
    )