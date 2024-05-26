from django.conf import settings

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound,PermissionDenied
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from .serializer import StoreListSerializer, SellingListSerializer, StoreDetailSerializer, StorePostSerializer
from .models import Store, SellList
from reviews.serializers import ReviewSerializer
from medias.serializer import PhotoSerializer

class SellingList(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_store = SellList.objects.all()
        serializer = SellingListSerializer(all_store, many=True, context={'request': request})
        return Response(serializer.data)
    
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

    def get(self, request, pk):
        sell_list = self.get_object(pk)
        serializer = SellingListSerializer(sell_list)
        return Response(serializer.data)
    
    def put(self, request, pk):
        sell_list = self.get_object(pk)
        serializer = SellingListSerializer(sell_list, data=request.data, partial=True)
        if serializer.is_valid():
            update_sell_list = serializer.save()
            return Response(SellingListSerializer(update_sell_list).data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

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
    
    # post 생성

class Stores(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        print(request.GET.get('type')) #None이면 전체, 음식점, 카페, 기타

        all_store = Store.objects.all()
        serializer = StoreListSerializer(all_store, many=True, context={'request': request})
        print(Response(serializer.data))
        return Response(serializer.data)
    
    def post(self, request):
        serializer = StorePostSerializer(data=request.data)

        if serializer.is_valid():
            sell_list = request.data.get('sell_list')
            
            if sell_list is not None:
                store = serializer.save(owner=request.user)
                for sell_list_pk in sell_list:
                    try:
                        selling = SellList.objects.get(pk=sell_list_pk)
                        store.sell_list.add(selling)
                    except SellList.DoesNotExist:
                        return Response({"error": f"{sell_list_pk}가 존재하지 않습니다."}, status=HTTP_400_BAD_REQUEST)
                
                serializer = StorePostSerializer(store, context={"request": request})
                return Response(serializer.data)
            else:
                return Response({"error": "판매 물건이 필요합니다."}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class StoresDetail(APIView):
    # 다른 사람 접근 금지
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        store = self.get_object(pk)
        serializer = StoreDetailSerializer(store, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        store = self.get_object(pk)
        if store.owner != request.user:
            raise PermissionDenied
        serializer = StoreDetailSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            update_store = serializer.save()
            return Response(StoreDetailSerializer(update_store).data)
        else:
            return Response(serializer.errors)
        
    def delete(self, request, pk):
        store = self.get_object(pk)
        if store.owner != request.user:
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

    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(  # serializer에 추가적인 데이터 보내기
                user=request.user,
                store=self.get_object(pk))
            serializer = ReviewSerializer(review)
            return Response(serializer.data)

class StorePhotos(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        store = self.get_object(pk)
        if request.user != store.owner:
            raise PermissionDenied

        serializer = PhotoSerializer(data=request.data)

        if serializer.is_valid():
            photo = serializer.save(store=store)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)