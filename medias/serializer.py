from rest_framework.serializers import ModelSerializer
from .models import Photo, ReviewsPhoto
from users.serializer import TinyUserSerializer

class PhotoSerializer(ModelSerializer):
    class Meta:
        model = Photo
        fields = (
            "pk",  # 기본키가 읽기 전용인 것을 안다.
            "file",
        )

class ReviewPhotoSerializer(ModelSerializer):
    class Meta:
        model = ReviewsPhoto
        fields = (
            "pk",  # 기본키가 읽기 전용인 것을 안다.
            "file",
        )