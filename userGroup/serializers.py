from rest_framework.serializers import ModelSerializer
from .models import Group, SharedList
from users.serializer import TinyUserSerializer
from stores.serializer import StoreSerializer
from rest_framework import serializers


class GroupSerializer(ModelSerializer):
    members = TinyUserSerializer(many=True, read_only=True)
    owner = TinyUserSerializer(read_only=True)
    class Meta:
        model = Group
        fields = (
            "pk",
            "name",
            "members",
            "owner"
        )

class MakeGroupSerializer(ModelSerializer):

    class Meta:
        model = Group
        fields = ("pk", "name", "members")



class GroupDetailSerializer(ModelSerializer):

    members = TinyUserSerializer(many=True, read_only=False)
    store = serializers.SerializerMethodField()
    owner = TinyUserSerializer(read_only=True)
    
    def get_store(self, obj):
        shared_lists = SharedList.objects.filter(group=obj)
        store_names = [store.name for store_list in shared_lists for store in store_list.store.all()]
        return store_names

    class Meta:
        model = Group
        fields = ("pk", "name", "members", "owner", "store", "updated_at")