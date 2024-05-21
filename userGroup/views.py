from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Group
from stores.models import Store
from .serializers import GroupSerializer, MakeGroupSerializer
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
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