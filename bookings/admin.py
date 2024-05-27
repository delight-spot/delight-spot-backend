from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "store_names", "created_at")

    def store_names(self, obj):
        return ", ".join([store.name for store in obj.store.all()])
    store_names.short_description = "Stores"