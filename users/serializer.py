from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User 

class TinyUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "avatar",
            "username"
        )
    
class PrivateUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("pk", "username", "name", "email", "avatar", "gender", "date_joined", "is_host")
        # exclude = (
        #     "password",
        #     "is_superuser",
        #     "is_staff",
        #     "is_active",
        #     "first_name",
        #     "last_name",
        #     "groups",
        #     "user_permissions",
        # )
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class NoticeUser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "avatar",
            "username",
            "is_host",
            )