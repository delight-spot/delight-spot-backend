from rest_framework import serializers
from .models import Reviews
from users.serializer import TinyUserSerializer

class ReviewSerializer(serializers.ModelSerializer):

    user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Reviews
        fields = (
            "pk",
            "user",
            # "rating",
            "total_rating",
            "taste_rating",
            "atmosphere_rating",
            "kindness_rating",
            "clean_rating",
            "parking_rating",
            "restroom_rating",
            "description"
            )