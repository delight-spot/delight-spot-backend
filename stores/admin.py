from django.contrib import admin
from .models import Store, SellList


@admin.register(Store)
class RoomAdmin(admin.ModelAdmin):

    # actions = (reset_prices,)

    list_display = (
        "name",
        "kind_menu",
        "total_rate",
        "taste_rate",
        "atmosphere_rate",
        "kindness_rate",
        "clean_rate",
        "parking_rate",
        "restroom_rate",
        "city",
        "created_at",
    )
    list_filter = (
        "city",
        "pet_friendly",
        "kind_menu",
        "created_at",
        "updated_at",
    )



@admin.register(SellList)
class SellistAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
