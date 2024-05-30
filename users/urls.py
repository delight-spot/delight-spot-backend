from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .views import (Me, Users, PublicUser, ChangePassword, LogOut, UserReviews, UserReviewDetail, UserStore, UserStoreDetail, KakaoLogin, JWTLogIn, JWTSignup)

urlpatterns = [
    path("users/log-out", LogOut.as_view()),
    path("users/jwt-login", JWTLogIn.as_view()),
    path("users/jwt-signup", JWTSignup.as_view()),
    path("users/kakao", KakaoLogin.as_view()),
    # path("users/token-login", obtain_auth_token),

    path("users", Users.as_view()),
    path("users/me", Me.as_view()),
    path("users/<str:username>", PublicUser.as_view()),
    
    path("users/change-password", ChangePassword.as_view()),
    path("users/<str:username>/reviews", UserReviews.as_view()),
    path("users/<str:username>/reviews/<int:pk>", UserReviewDetail.as_view()),
    path("users/<str:username>/stores", UserStore.as_view()),
    path("users/<str:username>/stores/<int:pk>", UserStoreDetail.as_view()),

]
