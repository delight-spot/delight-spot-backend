from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings
from .models import Notice
from .serializers import NoticeSerializer, PostNoticeSerializer, NoticeDetailSerializer
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

class NoticeViews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size        

        all_notice = Notice.objects.all()

        keyword = request.query_params.get('keyword')
        try:
            if keyword:
                all_notice = all_notice.filter(name__icontains=keyword)
        except ValueError:
            raise ParseError(detail="Invalid 'keyword' parameter value.")   

        all_notice = all_notice.order_by('-top_fixed', '-id')

        serializer = NoticeSerializer(
            all_notice.all()[start:end],
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
    
    def post(self, request):
        if not request.user.is_host:
            raise PermissionDenied(detail="You do not have permission to perform this action.")
        
        serializer = PostNoticeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
class NoticeDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Notice.objects.get(pk=pk)
        except Notice.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        notice = self.get_object(pk)
        serializer = NoticeDetailSerializer(notice, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        notice = self.get_object(pk)
        if not request.user.is_host:
            raise PermissionDenied("You do not have permission to edit this notice.")
        serializer = NoticeDetailSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            update_store = serializer.save()
            return Response(NoticeDetailSerializer(update_store).data)
        else:
            return Response(serializer.errors)
    
    def delete(self, request, pk):
        store = self.get_object(pk)
        if not request.user.is_host:
            raise PermissionDenied("You do not have permission to edit this notice.")
        store.delete()
        return Response(status=HTTP_204_NO_CONTENT)