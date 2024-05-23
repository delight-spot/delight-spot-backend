from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .views import (Me, Users, PublicUser, ChangePassword, LogIn, LogOut, UserReviews, UserReviewDetail, UserStore, UserStoreDetail)
#     SignUp,



urlpatterns = [
    path("", Users.as_view()),
    path("/me", Me.as_view()),
    path("/<str:username>", PublicUser.as_view()),
    path("/change-password", ChangePassword.as_view()),
    path("/log-in", LogIn.as_view()),
    path("/log-out", LogOut.as_view()),
    path("/<str:username>/reviews", UserReviews.as_view()),
    path("/<str:username>/reviews/<int:pk>", UserReviewDetail.as_view()),
    path("/<str:username>/stores", UserStore.as_view()),
    path("/<str:username>/stores/<int:pk>", UserStoreDetail.as_view()),

    path("token-login", obtain_auth_token),
]
