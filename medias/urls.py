from django.urls import path
from .views import PhotoDetail
# GetUploadURL, UploadPhoto

urlpatterns = [
    path("/photos/<int:pk>", PhotoDetail.as_view()),
    # path("photos/get-url", GetUploadURL.as_view()),
    # path("photos/upload-photo", UploadPhoto.as_view()),
]
