from django.urls import path
from .views import GroupList, GroupDetail, GroupStoreToggle, GroupUserToggle


urlpatterns = [
    path("", GroupList.as_view()),
    path("/<int:pk>", GroupDetail.as_view()),
    path("/<int:pk>/stores/<int:store_pk>", GroupStoreToggle.as_view()),
    path("/<int:pk>/users/<str:username>", GroupUserToggle.as_view()),
]
