from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Store, SellList
from medias.serializer import PhotoSerializer
from users.serializer import TinyUserSerializer
from bookings.models import Booking

class SellingListSerializer(ModelSerializer):
    class Meta:
        model = SellList
        fields = (
            "pk",
            "name",
            "description",
            "created_at"
        )

# bookings 전체 조회
class StoreSerializer(ModelSerializer):
    
    total_rating = serializers.SerializerMethodField()
    taste_rating = serializers.SerializerMethodField()
    atmosphere_rating = serializers.SerializerMethodField()
    kindness_rating = serializers.SerializerMethodField()
    clean_rating = serializers.SerializerMethodField()
    parking_rating = serializers.SerializerMethodField()
    restroom_rating = serializers.SerializerMethodField()

    reviews_len = serializers.SerializerMethodField()
    sell_list = SellingListSerializer(read_only=True, many=True)
    name = serializers.CharField()  # 추가: name 필드를 정의해야 함
    
    def get_total_rating(self, store):
        return store.total_rate()

    def get_taste_rating(self, store):
        return store.taste_rate()
    
    def get_atmosphere_rating(self, store):
        return store.atmosphere_rate()
    
    def get_kindness_rating(self, store):
        return store.kindness_rate()
    
    def get_clean_rating(self, store):
        return store.clean_rate()
    
    def get_parking_rating(self, store):
        return store.parking_rate()
    
    def get_restroom_rating(self, store):
        return store.restroom_rate()
    
    def get_reviews_len(self, store):
        return store.reviews_len()
    
    class Meta:
        model = Store
        fields = (
            "pk",
            "name",
            "kind_menu",
            "sell_list",
            "city",
            "reviews_len",
            "total_rating",
            "taste_rating",
            "atmosphere_rating",
            "kindness_rating",
            "clean_rating",
            "parking_rating",
            "restroom_rating",
            "created_at"
        )
    
class ListSerializer(ModelSerializer):

    # SerializerMethodField()를 사용하기 위해선
    # get_rating과 같이 이름이 특정한 모양을 가져야 한다. -> get_
    # 현재 serializing하고 있는 오브젝트와 함께 호출한다.
    
    total_rating = serializers.SerializerMethodField()
    taste_rating = serializers.SerializerMethodField()
    atmosphere_rating = serializers.SerializerMethodField()
    kindness_rating = serializers.SerializerMethodField()
    clean_rating = serializers.SerializerMethodField()
    parking_rating = serializers.SerializerMethodField()
    restroom_rating = serializers.SerializerMethodField()

    reviews_len = serializers.SerializerMethodField()
    sell_list = SellingListSerializer(read_only=True, many=True)
    # 역접근자는 위험하다 -> 방 하나에 수 천, 수 만개의 특성을 가지고 있을 수 있기 때문이다. -> pagination이 있어야 한다.
    photos = PhotoSerializer(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()

    def get_total_rating(self, store):
        return store.total_rate()

    def get_taste_rating(self, store):
        return store.taste_rate()
    
    def get_atmosphere_rating(self, store):
        return store.atmosphere_rate()
    
    def get_kindness_rating(self, store):
        return store.kindness_rate()
    
    def get_clean_rating(self, store):
        return store.clean_rate()
    
    def get_parking_rating(self, store):
        return store.parking_rate()
    
    def get_restroom_rating(self, store):
        return store.restroom_rate()
    
    def get_reviews_len(self, store):
        return store.reviews_len()

    def get_is_owner(self, store):
        request = self.context["request"]
        return store.owner == request.user

    class Meta:
        model = Store
        fields = (
            "pk",
            "name",
            "description",
            "kind_menu",
            "sell_list",
            "city",
            "reviews_len",
            
            "total_rating",
            "taste_rating",
            "atmosphere_rating",
            "kindness_rating",
            "clean_rating",
            "parking_rating",
            "restroom_rating",

            "photos",
            "is_owner",
            "created_at"
        )

class StoreListSerializer(ModelSerializer):

    total_rating = serializers.SerializerMethodField()
    # taste_rating = serializers.SerializerMethodField()
    # atmosphere_rating = serializers.SerializerMethodField()
    # kindness_rating = serializers.SerializerMethodField()
    # clean_rating = serializers.SerializerMethodField()
    # parking_rating = serializers.SerializerMethodField()
    # restroom_rating = serializers.SerializerMethodField()


    reviews_len = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    sell_list = SellingListSerializer(read_only=True, many=True)
    # 역접근자는 위험하다 -> 방 하나에 수 천, 수 만개의 특성을 가지고 있을 수 있기 때문이다. -> pagination이 있어야 한다.
    photos = PhotoSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, store):
        return store.owner.username


    def get_total_rating(self, store):
        return store.total_rate()

    # def get_taste_rating(self, store):
    #     return store.taste_rate()
    
    # def get_atmosphere_rating(self, store):
    #     return store.atmosphere_rate()
    
    # def get_kindness_rating(self, store):
    #     return store.kindness_rate()
    
    # def get_clean_rating(self, store):
    #     return store.clean_rate()
    
    # def get_parking_rating(self, store):
    #     return store.parking_rate()
    
    # def get_restroom_rating(self, store):
    #     return store.restroom_rate()
    

    def get_reviews_len(self, store):
        return store.reviews_len()

    def get_is_owner(self, store):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return store.owner == request.user
        return False

    def get_is_liked(self, store):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return Booking.objects.filter(user=request.user, store__pk=store.pk).exists()
        return False

    class Meta:
        model = Store
        fields = (
            "pk",
            "name",
            "description",
            "kind_menu",
            "sell_list",
            "city",
            "reviews_len",

            "total_rating",
            # "taste_rating",
            # "atmosphere_rating",
            # "kindness_rating",
            # "clean_rating",
            # "parking_rating",
            # "restroom_rating",

            "is_owner",
            "user_name",
            "is_liked",
            "photos",
            "created_at"
        )
        # depth = 1  # 모델의 모든 관계 확장 / 커스터마이즈 할 수 없다.

class StorePostSerializer(ModelSerializer):
    
    owner = TinyUserSerializer(read_only=True)
    sell_list = SellingListSerializer(
        read_only=True,
        many=True,
    )

    is_owner = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = (
            "pk",
            "owner",
            "name",
            "description",
            "kind_menu",
            "sell_list",
            "pet_friendly",
            "city",
            "is_owner",
            "photos",
        )

    def get_is_owner(self, store):
        request = self.context.get("request")
        if request:
            return store.owner == request.user
        return False

class StoreDetailSerializer(ModelSerializer):
    
    owner = TinyUserSerializer(read_only=True)
    sell_list = SellingListSerializer(many=True)
    
    total_rating = serializers.SerializerMethodField()
    taste_rating = serializers.SerializerMethodField()
    atmosphere_rating = serializers.SerializerMethodField()
    kindness_rating = serializers.SerializerMethodField()
    clean_rating = serializers.SerializerMethodField()
    parking_rating = serializers.SerializerMethodField()
    restroom_rating = serializers.SerializerMethodField()

    is_owner = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = "__all__"

    def get_total_rating(self, store):
        return store.total_rate()

    def get_taste_rating(self, store):
        return store.taste_rate()
    
    def get_atmosphere_rating(self, store):
        return store.atmosphere_rate()
    
    def get_kindness_rating(self, store):
        return store.kindness_rate()
    
    def get_clean_rating(self, store):
        return store.clean_rate()
    
    def get_parking_rating(self, store):
        return store.parking_rate()
    
    def get_restroom_rating(self, store):
        return store.restroom_rate()

    def get_is_owner(self, store):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return store.owner == request.user
        return False

    def get_is_liked(self, store):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return Booking.objects.filter(user=request.user, store__pk=store.pk).exists()
        return False
        # user가 만든 wishlist 중에 room id가 있는 room list를 포함한 wishlist를 찾아 pk가 room pk랑 일치하는 store를 찾는다.

    
class BookingStoreList(ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    class Meta:
        model = Store
        fields = ("pk", "name", "total_rate", "photos", "is_liked", "created_at")

    def get_is_liked(self, store):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return Booking.objects.filter(user=request.user, store__pk=store.pk).exists()
        return False
    
class GroupStoreList(ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    class Meta:
        model = Store
        fields = ("pk", "name", "photos", "created_at", "updated_at")
        