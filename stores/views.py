from django.conf import settings
from django.db.models import Count, Avg, F, Q

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound,PermissionDenied,ParseError,AuthenticationFailed
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
import jwt
from .serializer import StoreListSerializer, SellingListSerializer, StoreDetailSerializer, StorePostSerializer
from .models import Store, SellList
from reviews.serializers import ReviewSerializer, ReviewDetailSerializer

# swagger 추가
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SellingList(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    # swagger 추가
    @swagger_auto_schema(
        operation_description="Retrieve all selling lists",
        responses={200: SellingListSerializer(many=True)}
    )

    def get(self, request):
        all_store = SellList.objects.all()
        serializer = SellingListSerializer(all_store, many=True, context={'request': request})
        return Response(serializer.data)
    
    # swagger
    @swagger_auto_schema(
        operation_description="Create a new selling list",
        request_body=SellingListSerializer,
        responses={201: SellingListSerializer, 400: "Bad Request"}
    )

    def post(self, request):
        serializer = SellingListSerializer(data=request.data)
        if serializer.is_valid():
            new_selling = serializer.save()
            return Response(SellingListSerializer(new_selling).data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class SellingListDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return SellList.objects.get(pk=pk)
        except SellList.DoesNotExist:
            raise NotFound

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve a selling list by its ID",
        responses={200: SellingListSerializer, 404: "Not Found"}
    )

    def get(self, request, pk):
        sell_list = self.get_object(pk)
        serializer = SellingListSerializer(sell_list)
        return Response(serializer.data)
    
    # swagger
    @swagger_auto_schema(
        operation_description="Update a selling list by its ID",
        request_body=SellingListSerializer,
        responses={200: SellingListSerializer, 400: "Bad Request"}
    )

    def put(self, request, pk):
        sell_list = self.get_object(pk)
        serializer = SellingListSerializer(sell_list, data=request.data, partial=True)
        if serializer.is_valid():
            update_sell_list = serializer.save()
            return Response(SellingListSerializer(update_sell_list).data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    # swagger
    @swagger_auto_schema(
        operation_description="Delete a selling list by its ID",
        responses={204: "No Content"}
    )

    def delete(self, request, pk):
        sell_list = self.get_object(pk)
        sell_list.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    
# stores/pk/sellinglist
class SellingListView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound
        
    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve the selling list for a specific store",
        responses={200: SellingListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
        ]
    )

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        
        store = self.get_object(pk)
        serializer = SellingListSerializer(store.sell_list.all()[start:end], many=True)
        return Response(serializer.data)
    
    # swagger
    @swagger_auto_schema(
        operation_description="Add an item to the selling list for a specific store",
        request_body=SellingListSerializer,
        responses={201: SellingListSerializer, 400: "Bad Request"}
    )


    def post(self, request, pk):
        store = self.get_object(pk)
        sell_list_serializer = SellingListSerializer(data=request.data)
        if sell_list_serializer.is_valid():
            sell_list_serializer.save()
            store.sell_list.add(sell_list_serializer.instance)
            return Response(sell_list_serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(sell_list_serializer.errors, status=HTTP_400_BAD_REQUEST)

class Stores(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve all stores with optional filtering",
        responses={200: StoreListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('keyword', openapi.IN_QUERY, description="Keyword to search stores", type=openapi.TYPE_STRING),
            openapi.Parameter('type', openapi.IN_QUERY, description="Type of store", type=openapi.TYPE_STRING, multiple=True)
        ]
    )

    def get(self, request):
        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        all_store = Store.objects.all()

        # 검색 처리 :keyword = request.query_params.get('keyword')
        keyword = request.query_params.get('keyword')
        try:
            if keyword:
                all_store = all_store.filter(name__icontains=keyword)
        except ValueError:
            raise ParseError(detail="Invalid 'keyword' parameter value.")
        
        # 필터링 처리 :store_type = request.query_params.get('type')
        # store_types = request.query_params.getlist('type')
        # 필터링 처리
        store_types = request.query_params.getlist('type')
        valid_types = ['cafe', 'food', 'ect', 'rate', 'reviews']  # 유효한 type 값들
        # 요청받은 type 값들 중 유효하지 않은 값이 있다면 빈 리스트 반환
        if not all(store_type in valid_types for store_type in store_types):
            return Response([])  # 잘못된 type 값이 있을 경우 빈 리스트 반환

        filter_conditions = Q()
        annotate_conditions = {}

        for store_type in store_types:
            if store_type == 'cafe':
                filter_conditions &= Q(kind_menu='cafe')
            elif store_type == 'food':
                filter_conditions &= Q(kind_menu='food')
            elif store_type == 'ect':
                filter_conditions &= Q(kind_menu='ect')
            elif store_type == 'rate':
        # QuerySet에서는 모델의 메서드를 직접 정렬 기준으로 사용할 수 없어 annotate()를 사용하여 각 스토어의 평균 평점을 계산하고 이를 기준으로 정렬
                annotate_conditions['avg_rating'] = Avg(
                    F('reviews__taste_rating') +
                    F('reviews__atmosphere_rating') +
                    F('reviews__kindness_rating') +
                    F('reviews__clean_rating') +
                    F('reviews__parking_rating') +
                    F('reviews__restroom_rating')
                ) / 6.0
            elif store_type == 'reviews':
                annotate_conditions['review_count'] = Count('reviews')
            
        # 필터 조건 적용
        if filter_conditions:
            all_store = all_store.filter(filter_conditions)

        # annotate 조건 적용 및 정렬
        if 'avg_rating' in annotate_conditions and 'review_count' in annotate_conditions:
            all_store = all_store.annotate(**annotate_conditions).order_by('-avg_rating')
            # review_count를 기준으로 내림차순 정렬하고, 그 다음으로 avg_rating을 기준으로 내림차순 정렬
        elif 'avg_rating' in annotate_conditions:
            all_store = all_store.annotate(**annotate_conditions).order_by('-avg_rating')
            # annotate_conditions에 'avg_rating'만 존재하는 경우, avg_rating을 기준으로 내림차순 정렬
        elif 'review_count' in annotate_conditions:
            all_store = all_store.annotate(**annotate_conditions).order_by('-review_count')

        serializer = StoreListSerializer(all_store[start:end], many=True, context={'request': request})
        return Response(serializer.data)
    
    # swagger
    @swagger_auto_schema(
        operation_description="Create a new store",
        request_body=StorePostSerializer,
        responses={201: StorePostSerializer, 400: "Bad Request"}
    )

    def post(self, request):
        serializer = StorePostSerializer(data=request.data)

        if serializer.is_valid():
            sell_list = request.data.get('sell_list')
            
            # Store 객체를 먼저 저장
            store = serializer.save(owner=request.user)

            # sell_list가 있을 때만 처리
            if sell_list is not None:
                for sell_list_pk in sell_list:
                    try:
                        selling = SellList.objects.get(pk=sell_list_pk)
                        store.sell_list.add(selling)
                    except SellList.DoesNotExist:
                        return Response({"error": f"{sell_list_pk}가 존재하지 않습니다."}, status=400)
                
            serializer = StorePostSerializer(store, context={"request": request})
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class StoresDetail(APIView):
    # 다른 사람 접근 금지
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve a store by its ID",
        responses={200: StoreDetailSerializer, 404: "Not Found"}
    )


    def get(self, request, pk):
        print(request.user)
        store = self.get_object(pk)
        serializer = StoreDetailSerializer(store, context={'request': request})
        return Response(serializer.data)

    # swagger
    @swagger_auto_schema(
        operation_description="Update a store by its ID",
        request_body=StoreDetailSerializer,
        responses={200: StoreDetailSerializer, 400: "Bad Request", 403: "Permission Denied"}
    )

    def put(self, request, pk):

        # 헤더에서 JWT 토큰 가져오기
        jwt_token = request.headers.get('Authorization')
        print(jwt_token)

        try:
            # JWT 토큰 디코드
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            kakao_id = payload['kakao_id']
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        store = self.get_object(pk)

        if store.owner.kakao_id != kakao_id:
            raise PermissionDenied
        
        serializer = StoreDetailSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            update_store = serializer.save()
            return Response(StoreDetailSerializer(update_store).data)
        else:
            return Response(serializer.errors)
        
    # swagger
    @swagger_auto_schema(
        operation_description="Delete a store by its ID",
        responses={204: "No Content", 403: "Permission Denied"}
    )
    
    def delete(self, request, pk):
        # 헤더에서 JWT 토큰 가져오기
        jwt_token = request.headers.get('Authorization')
        
        try:
            # JWT 토큰 디코드
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            kakao_id = payload['kakao_id']
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        
        store = self.get_object(pk)
        
        if store.owner.kakao_id != kakao_id:
            raise PermissionDenied
        
        store.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    

class StoreReviews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve reviews for a specific store",
        responses={200: ReviewSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
        ]
    )

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        
        store = self.get_object(pk)
        serializer = ReviewSerializer(store.reviews.all()[start:end], many=True)
        return Response(serializer.data)

    # swagger
    @swagger_auto_schema(
        operation_description="Create a review for a specific store",
        request_body=ReviewSerializer,
        responses={201: ReviewSerializer, 400: "Bad Request"}
    )

    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                store=self.get_object(pk)
            )
            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class StoreDetailReviews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound
        
    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve detailed reviews for a specific store",
        responses={200: ReviewDetailSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
        ]
    )

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        
        store = self.get_object(pk)
        serializer = ReviewDetailSerializer(store.reviews.all()[start:end], many=True)
        return Response(serializer.data)



# class StorePhotosToggle(APIView):

#     permission_classes = [IsAuthenticatedOrReadOnly]

#     def get_object(self, pk):
#         try:
#             return Store.objects.get(pk=pk)
#         except Store.DoesNotExist:
#             raise NotFound

#     def post(self, request, pk):

#         # 헤더에서 JWT 토큰 가져오기
#         jwt_token = request.headers.get('Authorization')
        
#         try:
#             # JWT 토큰 디코드
#             payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
#             kakao_id = payload['kakao_id']
#         except jwt.exceptions.InvalidTokenError:
#             raise AuthenticationFailed('Invalid token')
        
#         store = self.get_object(pk)
        
#         if store.owner.kakao_id != kakao_id:
#             raise PermissionDenied

#         serializer = PhotoSerializer(data=request.data)

#         if serializer.is_valid():
#             photo = serializer.save(store=store)
#             serializer = PhotoSerializer(photo)
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)