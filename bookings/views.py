from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied, AuthenticationFailed
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.conf import settings
from django.db.models import Prefetch #모델을 통해 직접 필터링하는 방식
import jwt

from .models import Booking
from .serializers import BookingSerializer, BookingStoreSerializer
from stores.models import Store

# swagger 추가
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class Bookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # swagger 추가
    @swagger_auto_schema(
        operation_description="Retrieve the list of stores the user has booked",
        responses={200: BookingStoreSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('keyword', openapi.IN_QUERY, description="Keyword to search stores", type=openapi.TYPE_STRING),
            openapi.Parameter('type', openapi.IN_QUERY, description="Type of store", type=openapi.TYPE_STRING, multiple=True),
        ]
    )


    def get(self, request):
        # 헤더에서 JWT 토큰 가져오기
        jwt_token = request.headers.get('Authorization')
        
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            kakao_id = payload['kakao_id']
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        
        if request.user.kakao_id != kakao_id:
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
        # user_bookings = Booking.objects.filter(user__username=request.user.username).prefetch_related('store')
        user_bookings = Booking.objects.filter(user__kakao_id=kakao_id).prefetch_related('store')
        
        paginated_bookings = user_bookings[start:end]

        serializer = BookingSerializer(paginated_bookings, many=True, context={"request": request})
        return Response(serializer.data)



    # swagger 추가
    @swagger_auto_schema(
        operation_description="Create or toggle a booking for the user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'store_pk': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='List of store primary keys'
                )
            }
        ),
        responses={200: "OK", 400: "Bad Request"}
    )
    def post(self, request):
        store_pks = request.data.get('store_pk')
        if not isinstance(store_pks, list):
            return Response({"error": "store_pk must be a list"}, status=HTTP_400_BAD_REQUEST)
        
        user = request.user
        response_data = []

        for store_pk in store_pks:
            try:
                store = Store.objects.get(pk=store_pk)
                booking, created = Booking.objects.get_or_create(user=user)
                
                if booking.store.filter(pk=store_pk).exists():
                    booking.store.remove(store)
                    message = "Booking removed"
                    is_liked = False
                else:
                    booking.store.add(store)
                    message = "Booking added"
                    is_liked = True

                response_data.append({
                    "store_id": store_pk,
                    "is_liked": is_liked,
                    "message": message
                })
                
            except Store.DoesNotExist:
                return Response({"error": "Store not exist"}, status=HTTP_400_BAD_REQUEST)

        return Response({message}, status=HTTP_200_OK)