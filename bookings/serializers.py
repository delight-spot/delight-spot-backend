from rest_framework.serializers import ModelSerializer
from .models import Booking
from stores.serializer import StoreListSerializer, StoreSerializer


class BookingSerializer(ModelSerializer):
    store = StoreSerializer(read_only=True, many=True)
    # print(names)
    class Meta:
        model = Booking
        fields = ("pk","name", "store")

class BookingDetailSerializer(ModelSerializer):
    store = StoreListSerializer(read_only=True, many=True)
    # print(names)
    class Meta:
        model = Booking
        fields = ("pk", "name", "store")

