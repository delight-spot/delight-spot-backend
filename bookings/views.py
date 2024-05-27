from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
from django.conf import settings
from .models import Booking
from .serializers import BookingSerializer, BookingDetailSerializer
from stores.models import Store


class Bookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):

        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        
        all_reviews = Booking.objects.filter(user__username=request.user)
        serializer = BookingSerializer(
            all_reviews.all()[start:end],
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    

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

    def put(self, request, pk, stores_pk):
        bookings = self.get_list(pk, request.user)
        stores = self.get_store(stores_pk)
        if bookings.store.filter(pk=stores.pk).exists():
            bookings.store.remove(stores)
        else:
            bookings.store.add(stores)
        return Response(status=HTTP_200_OK)
        

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