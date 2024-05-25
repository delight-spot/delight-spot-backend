from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Group, SharedList
from stores.models import Store
from users.models import User
from .serializers import GroupSerializer, MakeGroupSerializer, GroupDetailSerializer
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN
from rest_framework.exceptions import NotFound,PermissionDenied
from django.conf import settings


class GroupList(APIView):

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
        all_group = Group.objects.all()
        serializer = GroupSerializer(all_group.all()[start:end], many=True, context={"request": request})
        return Response(serializer.data)  

    def post(self, request):
        serializer = MakeGroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save(user=request.user)
            serializer = MakeGroupSerializer(group)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
        

class GroupDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        group = self.get_object(pk)
        serializer = GroupDetailSerializer(group, context={'request': request})
        return Response(serializer.data)
    
    def delete(self, request, pk):
        group = self.get_object(pk)
        if group.owner != request.user:
            raise PermissionDenied
        group.delete()
        return Response(status=HTTP_204_NO_CONTENT)
            
class GroupStoreToggle(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_list(self, pk, owner):
        try:
            return SharedList.objects.get(group__pk=pk, group__owner=owner)
        except SharedList.DoesNotExist:
            raise NotFound

    def get_store(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound
        
    def put(self, request, pk, store_pk):
        storelist = self.get_list(pk, request.user)
        stores = self.get_store(store_pk)
        if storelist.store.filter(pk=stores.pk).exists():
            storelist.store.remove(stores)
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            storelist.store.add(stores)
            return Response(status=HTTP_200_OK)

class GroupUserToggle(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_owner(self, pk, owner):
        try:
            return Group.objects.get(pk=pk, owner=owner)
        except Group.DoesNotExist:
            raise NotFound
            
    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        
    def put(self, request, pk, username):
        owner = self.get_owner(pk, request.user)
        if owner.owner == request.user:
            user = self.get_user(username)
            if user in owner.members.all():
                owner.members.remove(user)
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                owner.members.add(user)
                return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_403_FORBIDDEN)