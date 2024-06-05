from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN
from rest_framework.exceptions import NotFound,PermissionDenied, ParseError
from django.conf import settings
from django.db.models import Q
from django.utils.functional import SimpleLazyObject

from .models import Group, SharedList
from stores.models import Store
from users.models import User
from .serializers import GroupSerializer, MakeGroupSerializer, GroupDetailSerializer


class GroupList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        # Q 객체는 Django의 ORM에서 복잡한 쿼리를 작성할 때 사용하는 도구, AND 및 OR 연산자를 사용하여 필터 조건을 결합 가능
        user_groups = Group.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()

        keyword = request.query_params.get('keyword')
        try:
            if keyword:
                user_groups = Group.objects.filter(Q(owner=request.user) | Q(members=request.user) & Q(name__icontains=keyword)).distinct()
        except ValueError:
            raise ParseError(detail="Invalid 'keyword' parameter value.")

        # 검색 결과가 없을 경우 전체 예약된 상점 목록으로 다시 설정
        if not user_groups.exists():
            user_groups = Group.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
            page = 1  # 페이지를 1로 초기화
            start = (page - 1) * page_size
            end = start + page_size

        # total_count = user_groups.count()
        # if start >= total_count:
        #     page = 1
        #     start = (page - 1) * page_size
        #     end = start + page_size

        paginated_groups = user_groups[start:end]

        serializer = GroupSerializer(paginated_groups, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = MakeGroupSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            group = serializer.save()  # owner는 create 메소드 내에서 처리됩니다.
            serializer = MakeGroupSerializer(group)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
        

class GroupDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, user, pk):
        try:
            group = Group.objects.get(pk=pk)
            if group.owner != user and user not in group.members.all():
                raise PermissionDenied("You do not have permission to access this group.")
            return group
        except Group.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        user = request.user
        if isinstance(user, SimpleLazyObject):
            user = User.objects.get(pk=user.pk)
        group = self.get_object(user, pk)
        serializer = GroupDetailSerializer(group, context={'request': request})
        return Response(serializer.data)
    
    def delete(self, request, pk):
        user = request.user
        if isinstance(user, SimpleLazyObject):
            user = User.objects.get(pk=user.pk)
        group = self.get_object(user, pk)
        if group.owner != user:
            raise PermissionDenied
        group.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class GroupStoreToggle(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_group(self, pk):
        try:
            return Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            raise NotFound

    def get_list(self, group):
        try:
            return SharedList.objects.get(group=group)
        except SharedList.DoesNotExist:
            raise NotFound

    def get_store(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise NotFound
        
    def put(self, request, pk, store_pk):
        group = self.get_group(pk)
        # Check if the requester is the group owner or a member of the group
        if request.user == group.owner or request.user in group.members.all():
            storelist = self.get_list(group)
            store = self.get_store(store_pk)
            # Check if the store is already in the list
            if storelist.store.filter(pk=store.pk).exists():
                storelist.store.remove(store)
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                storelist.store.add(store)
                return Response(status=HTTP_200_OK)
        else:
            return Response({"detail": "이 작업을 수행할 권한(permission)이 없습니다."}, status=HTTP_403_FORBIDDEN)


class GroupUserToggle(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_group(self, pk):
        try:
            return Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            raise NotFound

    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        
    def put(self, request, pk, username):
        group = self.get_group(pk)
        user = self.get_user(username)
        
        # 요청자가 그룹의 소유자이거나 멤버인지 확인
        if request.user == group.owner or request.user in group.members.all():
            # 사용자가 이미 멤버인지 확인
            if user in group.members.all():
                group.members.remove(user)
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                group.members.add(user)
                return Response(status=HTTP_200_OK)
        else:
            # print(f"Access denied for user: {request.user.username}")  # 디버깅 정보 추가
            return Response({"detail": "이 작업을 수행할 권한(permission)이 없습니다."}, status=HTTP_403_FORBIDDEN)