from rest_framework import serializers
from .models import Reviews
from users.serializer import TinyUserSerializer

class ReviewSerializer(serializers.ModelSerializer):

    user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Reviews
        fields = ("pk", "user", "rating", "description")