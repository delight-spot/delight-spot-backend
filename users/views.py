from django.conf import settings
import jwt
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.hashers import make_password

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework_simplejwt.tokens import RefreshToken

import requests
from .serializer import UserSerializer # RegisterSerializer, 
from .models import User
from reviews.models import Reviews
from reviews.serializers import ReviewSerializer
from stores.models import Store
from stores.serializer import StoreDetailSerializer
from .serializer import PrivateUserSerializer
import os
import environ
from pathlib import Path



class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(PrivateUserSerializer(user).data)

    def put(self, request):
        user = request.user
        data = request.data
        
        if 'is_host' in data:
            if not user.is_host:
                return Response({"detail": "You do not have permission to change 'is_host' field."}, status=HTTP_403_FORBIDDEN)    

        serializer = PrivateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            new_user = serializer.save()
            serializer = PrivateUserSerializer(new_user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class Users(APIView):

    def post(self, request):
        password = request.data.get("password")
        if not password:
            raise ParseError
        
        serializer = PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()
            serializer = PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PublicUser(APIView):

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        serializer = PrivateUserSerializer(user)
        return Response(serializer.data)


class UserReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, username):

        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        all_reviews = Reviews.objects.filter(user__username=username)

        
        serializer = ReviewSerializer(
            all_reviews.all()[start:end],
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
# # __ 은 관계를 나타내는 Django ORN,
# # Reviews.objects.filter(user__username=username) -> Reviews 모델에서 user가 username인 것에 접근

class UserReviewDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_list(self, pk, user):
        try:
            return Reviews.objects.get(pk=pk, user=user)
        except Reviews.DoesNotExist:
            raise NotFound

    def get(self, request, pk, username):  # username 인자 추가
        
        review = self.get_list(pk, request.user)
        serializer = ReviewSerializer(review, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk, username):
        review = self.get_list(pk, request.user)
        serializer = ReviewSerializer(
            review,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_wishlist = serializer.save()
            serializer = ReviewSerializer(update_wishlist)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    def delete(self, request, pk, username):
        review = self.get_list(pk, request.user)
        review.delete()
        return Response(status=HTTP_200_OK)

class UserStore(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, username):

        try:
            page = request.query_params.get("page", 1) # page를 찾을 수 없다면 1 page
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        all_stores = Store.objects.filter(owner__username=username)
        serializer = StoreDetailSerializer(
            all_stores.all()[start:end],
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
# # context={"request": request}
# # Serializer의 context에 'request' 키가 없기 때문에 발생 -> request 객체를 serializer로 전달하지 않았을 때 발생
# # View에서 Serializer를 사용할 때 context에 request 객체를 넣어서 Serializer에 전달하는 것이 일반적
# # 왜?  여러 개의 객체가 포함된 QuerySet => <QuerySet [<Room: 뭉치네>, <Room: 루루네>, <Room: zzone House>]>
# # 쿼리셋이 여러 개의 객체를 반환하는 경우에는 context={'request': request}와 같이 request 객체를 전달하는 것을 권장

class UserStoreDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_list(self, pk, user):
        try:
            return Store.objects.get(pk=pk, owner=user)
        except Store.DoesNotExist:
            raise NotFound

    def get(self, request, pk, username):  # username 인자 추가
        review = self.get_list(pk, request.user)
        serializer = StoreDetailSerializer(review, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk, username):
        review = self.get_list(pk, request.user)
        serializer = StoreDetailSerializer(
            review,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            update_wishlist = serializer.save()
            serializer = StoreDetailSerializer(update_wishlist)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    def delete(self, request, pk, username):
        review = self.get_list(pk, request.user)
        review.delete()
        return Response(status=HTTP_200_OK)


class ChangePassword(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:
            login(request, user)
            return Response({"ok": "welcome"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "wrong password"}, status=status.HTTP_400_BAD_REQUEST
            )


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": "bye"})


env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

class JWTLogIn(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError

        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            token = jwt.encode(
                {"pk": user.pk},
                env("SECRET_KEY"),
                algorithm="HS256",
            )
            return Response({"token": token})
        else:
            return Response({"error": "wrong password"})


class JWTSignup(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(email=request.data['email']).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class KakaoLogin(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            access_token = requests.post(
                "https://kauth.kakao.com/oauth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": "583f1ebb47209c90313ca9808363f605",
                    "redirect_uri": "http://127.0.0.1:3000/social/kakao",
                    "code": code,
                },
            )
            print(access_token.json(), "\n")
            # 서버가 카카오 서버로 인가 코드 받기 요청 -> 사용자에게 카카오계정 로그인 요청 -> 사용자가 로그인 -> 동의화면 -> Redirect URI로 인가 코드 전달
            # 서버가 Redirect URI로 전달받은 인가 코드로 토큰 받기 요청 -> 카카오가 토큰 발급해 서버에 전달
            # 발급받은 액세스 토큰으로 사용자 정보 가져오기를 요청해 사용자의 회원번호 및 정보를 조회해 서비스 회원인지 확인

            access_token = access_token.json().get("access_token")
            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            user_data = user_data.json()
            print(user_data, "\n")

            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            print(profile)

            try:
                user = User.objects.get(username=profile.get("nickname"))
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=profile.get("nickname"),
                    name=profile.get("nickname"),
                    avatar=profile.get("profile_image_url"),
                )
                user.set_unusable_password()  # 이 유저는 password로 로근인을 할 수 없기 때문에 설정 / .has_usable_password
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
