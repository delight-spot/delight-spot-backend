from django.urls import path
from . import views

urlpatterns = [
    path('stores', views.Stores.as_view()),
    path("stores/<int:pk>", views.StoresDetail.as_view()),
    path("stores/<int:pk>/sellinglists", views.SellingListView.as_view()),
    path("stores/sellinglists/<int:pk>", views.SellingListDetail.as_view()),

    path("stores/<int:pk>/reviews", views.StoreReviews.as_view()),
    path("stores/<int:pk>/photos", views.StorePhotosToggle.as_view()),

    # path("/sellinglists", views.SellingList.as_view()),
]