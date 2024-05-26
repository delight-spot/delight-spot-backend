from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Booking
from stores.models import Store
from .serializers import BookingSerializer, BookingDetailSerializer
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
from django.conf import settings


class Bookings(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        
        # request.user와 동일한 유저가 가지고 있는 booking
        all_bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(all_bookings.all()[start:end], many=True, context={"request": request})
        return Response(serializer.data)  

    def post(self, request):
        serializer = BookingSerializer(data=request.data)

        if serializer.is_valid():
            # 사용자가 이미 동일한 종류의 예약을 했는지 확인
            existing_booking = Booking.objects.filter(
                user=request.user,
                kind=serializer.validated_data['kind'],
            ).first()
            
            if existing_booking:
                return Response({"error": "이미 찜한 가게가 있습니다."}, status=HTTP_400_BAD_REQUEST)

            serializer.save(user=request.user)
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    # delete

class BookingDetail(APIView):

    permission_classes = [IsAuthenticated]

    # 해당 유저만 볼 수 있다. -> user 필요
    def get_object(self, pk, user):
        try:
            return Booking.objects.get(pk=pk, user=user)
        except Booking.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        serializer = BookingDetailSerializer(
            wishlist,
            context={"request": request},
        )
        return Response(serializer.data)

    def delete(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        wishlist.delete()
        return Response(status=HTTP_200_OK)

    def put(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        serializer = BookingDetailSerializer(
            wishlist,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_wishlist = serializer.save()
            serializer = BookingDetailSerializer(update_wishlist)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class BookingToggle(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_list(self, pk, user):
        try:
            return Booking.objects.get(pk=pk, user=user)
        except Booking.DoesNotExist:
            raise NotFound

    def get_store(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound

    def put(self, request, pk, store_pk):
        booklist = self.get_list(pk, request.user)
        stores = self.get_store(store_pk)
        if booklist.store.filter(pk=stores.pk).exists():
            booklist.store.remove(stores)
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            booklist.store.add(stores)
            return Response(status=HTTP_200_OK)
        
