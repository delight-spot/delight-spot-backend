from rest_framework.serializers import ModelSerializer
from .models import Group
from users.serializer import TinyUserSerializer
from rest_framework import serializers


class GroupSerializer(ModelSerializer):

    class Meta:
        model = Group
        fields = (
            "pk",
            "name",
            "members",
        )

class MakeGroupSerializer(ModelSerializer):

    class Meta:
        model = Group
        fields = ("pk", "name", "members")