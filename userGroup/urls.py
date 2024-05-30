from django.urls import path
from .views import GroupList, GroupDetail, GroupStoreToggle, GroupUserToggle


urlpatterns = [
    path("groups", GroupList.as_view()),
    path("groups/<int:pk>", GroupDetail.as_view()),
    path("groups/<int:pk>/stores/<int:store_pk>", GroupStoreToggle.as_view()),
    path("groups/<int:pk>/users/<str:username>", GroupUserToggle.as_view()),
]
