from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from django.conf import settings
from django.db.models import Prefetch #모델을 통해 직접 필터링하는 방식

from .models import Booking
from .serializers import BookingSerializer, BookingStoreSerializer
from stores.models import Store


class Bookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, username):

        if request.user.username != username:
            raise PermissionDenied(detail="접근 권한이 없습니다.")

        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        # 사용자의 모든 예약된 상점 가져오기
        # prefetch_related: 조인을 하지 않고 개별 쿼리를 실행 후, django에서 직접 데이터 조합
        user_bookings = Booking.objects.filter(user__username=username).prefetch_related('store')
        
        # 상점 리스트를 직접 구성하는 대신, 상점에 대한 쿼리셋을 사용
        store_ids = []
        for booking in user_bookings:
            store_ids.extend(booking.store.values_list('id', flat=True))

        # 상점 쿼리셋을 구성합니다.
        store_queryset = Store.objects.filter(id__in=store_ids)

        # 필터링 처리
        keyword = request.query_params.get('keyword')
        try:
            if keyword:
                store_queryset = store_queryset.filter(name__icontains=keyword)
        except ValueError:
            raise ParseError(detail="Invalid 'keyword' parameter value.")

        store_types = request.query_params.getlist('type')
        try:
            if store_types:
                store_queryset = store_queryset.filter(kind_menu__in=store_types)
        except ValueError:
            raise ParseError(detail="Invalid 'type' parameter value.")
        
        # 검색 결과가 없을 경우 전체 예약된 상점 목록으로 다시 설정
        if not store_queryset.exists():
            store_queryset = Store.objects.filter(id__in=store_ids)
            page = 1  # 페이지를 1로 초기화
            start = (page - 1) * page_size
            end = start + page_size

        # 페이지네이션 처리
        total_count = store_queryset.count()
        if start >= total_count:  # 페이지네이션 범위를 벗어난 경우 초기화
            page = 1
            start = (page - 1) * page_size
            end = start + page_size

        paginated_stores = store_queryset[start:end]

        serializer = BookingStoreSerializer(paginated_stores, many=True, context={"request": request})
        return Response(serializer.data)
    
    def post(self, request, username):
        user_bookings = Booking.objects.filter(user=request.user)

        if user_bookings.exists():
            # booking 목록이 이미 존재하는 경우 BookingToggle의 put 메서드를 호출
            store_pks = request.data.get('store_pk')
            if not isinstance(store_pks, list):
                return Response({"error": "store_pk must be a list"}, status=HTTP_400_BAD_REQUEST)
            
            booking_toggle = BookingToggle()
            return booking_toggle.handle_toggle(request, store_pks)

        # booking 목록이 존재하지 않는 경우 새로운 예약 목록을 생성
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            wishlist = serializer.save(user=request.user)
            serializer = BookingSerializer(wishlist)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class BookingToggle(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_list(self, user):
        return Booking.objects.filter(user=user)

    def get_store(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound("Store not found")

    def handle_toggle(self, request, store_pks):
        bookings = self.get_list(request.user)  # Get all bookings for the user
        action = "added"

        for store_pk in store_pks:
            store = self.get_store(store_pk)  # Get the store object

            has_store = False
            for booking in bookings:
                if booking.store.filter(pk=store.pk).exists():
                    booking.store.remove(store)
                    action = "removed"
                    has_store = True
                booking.save()
            
            if not has_store:
                if bookings.exists():
                    booking = bookings.first()
                else:
                    booking = Booking.objects.create(user=request.user)  # Create a new Booking object
                booking.store.add(store)
                booking.save()

        return Response({"status": "success", "action": action}, status=HTTP_200_OK)

    def put(self, request, store_pk, username):
        return self.handle_toggle(request, [store_pk])
