from rest_framework.serializers import ModelSerializer
from .models import Photo


class PhotoSerializer(ModelSerializer):
    class Meta:
        model = Photo
        fields = (
            "pk",  # 기본키가 읽기 전용인 것을 안다.
            "file",
            "description",
        )
