from django.urls import path
from .views import GroupList


urlpatterns = [
    path("", GroupList.as_view()),
    # path("<int:pk>", WishlistDetail.as_view()),
    # path("<int:pk>/rooms/<int:room_pk>", WishlistToggle.as_view()),
]
