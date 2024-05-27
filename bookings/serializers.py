from rest_framework.serializers import ModelSerializer
from .models import Booking
from stores.serializer import StoreListSerializer, StoreSerializer, BookingStoreList
from users.serializer import TinyUserSerializer


class BookingSerializer(ModelSerializer):
    store = BookingStoreList(read_only=True, many=True)
    user = TinyUserSerializer(read_only=True)
    # print(names)
    class Meta:
        model = Booking
        fields = ("pk","user", "store")

class BookingDetailSerializer(ModelSerializer):
    store = StoreListSerializer(read_only=True, many=True)
    # print(names)
    class Meta:
        model = Booking
        fields = ("pk", "user", "store")

