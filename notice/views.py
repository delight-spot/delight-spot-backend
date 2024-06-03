from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings
from .models import Notice
from .serializers import NoticeSerializer
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied


class NoticeViews(APIView):

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

        serializer = NoticeSerializer(
            all_notice.all()[start:end],
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)