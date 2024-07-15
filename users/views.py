from django.conf import settings
import jwt
from django.contrib.auth import login, authenticate, logout

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework_simplejwt.tokens import RefreshToken

import requests
from .serializer import UserSerializer
from .models import User
from reviews.models import Reviews
from reviews.serializers import ReviewSerializer
from stores.models import Store
from stores.serializer import StoreDetailSerializer, StoreListSerializer
from .serializer import PrivateUserSerializer, TinyUserSerializer
from bookings.models import Booking
import os
import environ
from pathlib import Path
import logging

# swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class Me(APIView):
    permission_classes = [IsAuthenticated]

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve the authenticated user's profile",
        responses={200: PrivateUserSerializer, 403: "Forbidden"}
    )

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "You do not have permission."}, status=HTTP_403_FORBIDDEN)
        serializer = PrivateUserSerializer(request.user)
        return Response(serializer.data)

    # swagger
    @swagger_auto_schema(
        operation_description="Update the authenticated user's profile",
        request_body=PrivateUserSerializer,
        responses={200: "OK", 400: "Bad Request", 403: "Forbidden"}
    )

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
            return Response("OK")
        else:
            return Response(serializer.errors)


class Users(APIView):

    # swagger
    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=PrivateUserSerializer,
        responses={201: "OK", 400: "Bad Request"}
    )

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
            return Response("OK")
        else:
            return Response(serializer.errors)


class PublicUser(APIView):

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve a public user profile by username",
        responses={200: TinyUserSerializer, 404: "Not Found"}
    )

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        serializer = TinyUserSerializer(user)
        return Response(serializer.data)


class UserReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve reviews written by a specific user",
        responses={200: ReviewSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
        ]
    )

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
            return Reviews.objects.get(pk=pk)
        except Reviews.DoesNotExist:
            raise NotFound

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve a specific review by ID for a specific user",
        responses={200: ReviewSerializer, 404: "Not Found"}
    )
    def get(self, request, pk, username):
        review = self.get_list(pk, request.user)
        serializer = ReviewSerializer(review, context={"request": request})
        return Response(serializer.data)

    # swagger
    @swagger_auto_schema(
        operation_description="Update a specific review by ID for a specific user",
        request_body=ReviewSerializer,
        responses={200: "OK", 400: "Bad Request"}
    )
    def put(self, request, pk, username):
        try:
            review = self.get_list(pk, request.user)
            if review.user != request.user:
                return Response({"error": "You do not have permission to modify this review."}, status=status.HTTP_403_FORBIDDEN)
        except Reviews.DoesNotExist:
            return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        review_data = request.data.get('reviewData', {})
        review_data['id'] = pk

        serializer = ReviewSerializer(
            review,
            data=review_data,
            partial=True,
        )
        print("request.data", request.data)

        if serializer.is_valid():
            update_reviews = serializer.save()
            print("ReviewSerializer(update_reviews).data",ReviewSerializer(update_reviews).data)
            # logger.info(f"Updated review: {update_reviews}")
            return Response(ReviewSerializer(update_reviews).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    # swagger
    @swagger_auto_schema(
        operation_description="Delete a specific review by ID for a specific user",
        responses={200: "OK", 404: "Not Found"}
    )
    def delete(self, request, pk, username):
        try:
            review = self.get_list(pk, request.user)
            if review.user != request.user:
                return Response({"error": "You do not have permission to delete this review."}, status=status.HTTP_403_FORBIDDEN)
        except Reviews.DoesNotExist:
            return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(status=status.HTTP_200_OK)

class UserStore(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve stores owned by a specific user",
        responses={200: StoreListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
        ]
    )

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
        serializer = StoreListSerializer(
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

    # swagger
    @swagger_auto_schema(
        operation_description="Retrieve a specific store by ID for a specific user",
        responses={200: StoreDetailSerializer, 404: "Not Found"}
    )

    def get(self, request, pk, username):  # username 인자 추가
        review = self.get_list(pk, request.user)
        serializer = StoreDetailSerializer(review, context={"request": request})
        return Response(serializer.data)

    # swagger
    @swagger_auto_schema(
        operation_description="Update a specific store by ID for a specific user",
        request_body=StoreDetailSerializer,
        responses={200: "OK", 400: "Bad Request"}
    )

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
            return Response("OK")
        else:
            return Response(serializer.errors)
        
    # swagger
    @swagger_auto_schema(
        operation_description="Delete a specific store by ID for a specific user",
        responses={200: "OK", 404: "Not Found"}
    )

    def delete(self, request, pk, username):
        review = self.get_list(pk, request.user)
        review.delete()
        return Response(status=HTTP_200_OK)


class ChangePassword(APIView):

    permission_classes = [IsAuthenticated]

    # swagger
    @swagger_auto_schema(
        operation_description="Change the authenticated user's password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Old password'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password')
            }
        ),
        responses={200: "OK", 400: "Bad Request"}
    )

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

    # swagger
    @swagger_auto_schema(
        operation_description="Authenticate a user and log them in",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
            }
        ),
        responses={200: "OK", 400: "Bad Request"}
    )

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

    # swagger
    @swagger_auto_schema(
        operation_description="Log out the authenticated user",
        responses={200: "OK"}
    )

    def post(self, request):
        logout(request)
        return Response({"ok": "bye"})


env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

class KakaoLogin(APIView):

    # swagger
    @swagger_auto_schema(
        operation_description="Log in using Kakao OAuth",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='Kakao authorization code')
            }
        ),
        responses={200: "OK", 400: "Bad Request"}
    )

    def post(self, request):
        try:
            code = request.data.get("code")

            if not code:
                return Response(
                    {"error": "Authorization code는 필수입니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
 
            access_token_response = requests.post(
                    "https://kauth.kakao.com/oauth/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "authorization_code",
                        "client_id": "583f1ebb47209c90313ca9808363f605",
                        "redirect_uri": "http://127.0.0.1:3000/social/kakao",
                        "code": code,
                    },
                )

            if access_token_response.status_code != 200:
                return Response(
                    access_token_response.json(), 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            access_token = access_token_response.json().get("access_token")
            refresh_token = access_token_response.json().get("refresh_token")

            if not access_token or not refresh_token:
                return Response(
                    {"error": "Access token 또는 Refresh token을 가져올 수 없습니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_data_response = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                }
            )

            if user_data_response.status_code != 200:
                return Response(
                    user_data_response.json(), 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_data = user_data_response.json()

            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            kakao_id = user_data.get("id")

            # 세션에 profile과 kakao_id 저장
            request.session['kakao_profile'] = profile
            request.session['kakao_id'] = kakao_id

            try:
                user = User.objects.get(kakao_id=kakao_id)
                login(request, user)

                # 유저에게 예약 목록이 있는지 확인하고, 없으면 생성
                self.ensure_user_has_booking_list(user)

                # JWT 토큰 생성
                payload = {'kakao_id': kakao_id}
                jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                return Response(status=status.HTTP_200_OK, data={'is_member': True, 'kakao_jwt': jwt_token})
            except User.DoesNotExist:
                return Response(status=status.HTTP_200_OK, data={'is_member': False})

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def ensure_user_has_booking_list(self, user):
        if not Booking.objects.filter(user=user).exists():
            Booking.objects.create(user=user)


class KakaoSignup(APIView):

    # swagger
    @swagger_auto_schema(
        operation_description="Sign up a new user using Kakao OAuth",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email')
            }
        ),
        responses={200: "OK", 400: "Bad Request"}
    )

    def post(self, request):
        try:
            email = request.data.get("email")
            if not email:
                return Response(
                    {"error": "이메일은 필수입니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            profile = request.session.get('kakao_profile')
            kakao_id = request.session.get('kakao_id')

            if not profile or not kakao_id:
                return Response(
                    {"error": "세션에서 필요한 데이터를 찾을 수 없습니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user, created = User.objects.get_or_create(
                kakao_id=kakao_id,
                defaults={
                    'username': profile.get("nickname"),
                    'name': profile.get("nickname"),
                    'avatar': profile.get("profile_image_url"),
                    'kakao_id': kakao_id,
                    'email': email
                }
            )

            if not created:
                user.kakao_id = kakao_id
                user.refresh_token = request.session.get('refresh_token')
                user.save()

            user.set_unusable_password()
            user.save()
            login(request, user)

            # 유저에게 예약 목록이 있는지 확인하고, 없으면 생성
            self.ensure_user_has_booking_list(user)

            payload = {'kakao_id': kakao_id}
            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return Response(status=status.HTTP_200_OK, data={'signup': True, 'kakao_jwt': jwt_token})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def ensure_user_has_booking_list(self, user):
        if not Booking.objects.filter(user=user).exists():
            Booking.objects.create(user=user)