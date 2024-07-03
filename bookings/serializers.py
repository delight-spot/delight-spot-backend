from rest_framework.serializers import ModelSerializer
from .models import Booking
from stores.serializer import StoreListSerializer, StoreSerializer, BookingStoreList
from users.serializer import TinyUserSerializer
from stores.serializer import BookingStoreList
from stores.models import Store


class BookingSerializer(ModelSerializer):
    store = BookingStoreList(read_only=True, many=True)
    user = TinyUserSerializer(read_only=True)
    # print(names)
    class Meta:
        model = Booking
        fields = ("pk","user", "store")

class BookingStoreSerializer(ModelSerializer):
    photos = BookingStoreList(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ("pk", "name", "photos",  "created_at")
