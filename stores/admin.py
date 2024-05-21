from django.contrib import admin
from .models import Store, SellList


# @admin.action(description="Set all pirces to zero")
# def reset_prices(model_admin, request, a):  # rooms
#     print(model_admin)
#     print(request)
#     print(a)
#     for room in a.all():
#         room.price = 0
#         room.save()


@admin.register(Store)
class RoomAdmin(admin.ModelAdmin):

    # actions = (reset_prices,)

    list_display = (
        "name",
        "kind_menu",
        "kind_detail",
        "rating",
        "city",
        "created_at",
    )
    list_filter = (
        "city",
        "pet_friendly",
        "kind_menu",
        "kind_detail",
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
