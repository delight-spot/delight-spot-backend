from django.urls import path
from . import views

urlpatterns = [

    path('', views.Stores.as_view()),

    # path("", views.Stores.as_view()),
    
    path("/<int:pk>", views.StoresDetail.as_view()),
    path("/<int:pk>/sellinglists", views.SellingListView.as_view()),
    path("/<int:pk>/reviews", views.StoreReviews.as_view()),
    path("/<int:pk>/photos", views.StorePhotos.as_view()),
    path("/sellinglists", views.SellingList.as_view()),
    path("/sellinglists/<int:pk>", views.SellingListDetail.as_view()),
]