from rest_framework import serializers
from users.serializer import NoticeUser
from .models import Notice

class NoticeSerializer(serializers.ModelSerializer):
    user = NoticeUser(read_only=True) # 유저 정보를 가져온다 !

    class Meta:
        model = Notice
        fields = ('pk', 'name', 'created_at', 'updated_at', 'top_fixed', 'user')


class NoticeDetailSerializer(serializers.ModelSerializer):
    user = NoticeUser(read_only=True)

    class Meta:
        model = Notice
        fields = "__all__"


class PostNoticeSerializer(serializers.ModelSerializer):
    user = NoticeUser(read_only=True) # 유저 정보를 가져온다 !

    class Meta:
        model = Notice
        fields = ('pk', 'name', 'top_fixed', 'description', 'user')