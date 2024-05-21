from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import Photo

from django.core.files.base import ContentFile

class PhotoDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise NotFound
        
    def delete(self, request, pk):
        photo = self.get_object(pk)

        if (photo.store and photo.store.owner != request.user):
            raise PermissionDenied
        photo.delete()
        return Response(status=HTTP_200_OK)
    

# class GetUploadURL(APIView):

#     def post(self, request):
#         if result:
#             return Response(
#                 {"id": result.get("id"), "uploadURL": result.get("uploadURL")}
#             )
#         else:
#             return Response(
#                 {
#                     "id": "00000",
#                     "uploadURL": "http://127.0.0.1:8000/api/v1/medias/photos/upload-photo",
#                 }
#             )


# class UploadPhoto(APIView):

#     def post(self, request):
#         image_data = request.FILES["file"]
#         path = default_storage.save(image_data, ContentFile(image_data.read()))
#         return Response({"result": {"id": path}})
