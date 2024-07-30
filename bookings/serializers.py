from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Booking
from stores.serializer import StoreListSerializer, StoreSerializer, BookingStoreList
from users.serializer import TinyUserSerializer
from stores.serializer import BookingStoreList
from stores.models import Store



class BookingStoreSerializer(ModelSerializer):
    photos = serializers.JSONField(required=False)

    class Meta:
        model = Store
        fields = ("pk", "name", "photos",  "created_at")

class BookingSerializer(ModelSerializer):
    store = BookingStoreList(read_only=True, many=True)
    # user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ("pk", "store")
