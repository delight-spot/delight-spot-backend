from rest_framework.serializers import ModelSerializer
from .models import Group, SharedList
from users.serializer import TinyUserSerializer
from stores.serializer import GroupStoreList
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
        fields = ("pk", "name")

    def create(self, validated_data):
        # context에서 request를 가져와서 request.user를 owner로 설정
        user = self.context['request'].user
        group = Group.objects.create(owner=user, **validated_data)
        return group



class GroupDetailSerializer(ModelSerializer):

    members = TinyUserSerializer(many=True, read_only=False)
    store = serializers.SerializerMethodField()
    owner = TinyUserSerializer(read_only=True)
    
    def get_store(self, obj):
        shared_lists = SharedList.objects.filter(group=obj)
        # store_names = [store.name for store_list in shared_lists for store in store_list.store.all()]
        # return store_names
        stores = [GroupStoreList(store_list.store.all(), many=True).data for store_list in shared_lists]
        return stores
    
    class Meta:
        model = Group
        fields = ("pk", "name", "members", "owner", "store", "updated_at")