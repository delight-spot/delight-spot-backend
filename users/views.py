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
from stores.serializer import StoreDetailSerializer, StoreListSerializer
from .serializer import PrivateUserSerializer, TinyUserSerializer
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
        serializer = TinyUserSerializer(user)
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
    


class KakaoLogin(APIView):
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
            
            print(access_token_response.json(), "\n")
            access_token = access_token_response.json().get("access_token")
            refresh_token = access_token_response.json().get("refresh_token")
            print(f"access_token: {access_token}, refresh_token: {refresh_token}")

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
            print(user_data, "\n")

            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            kakao_id = user_data.get("id")

            # 세션에 profile과 kakao_id 저장
            request.session['kakao_profile'] = profile
            request.session['kakao_id'] = kakao_id
            request.session['code'] = code

            print(kakao_id)

            try:
                user = User.objects.get(kakao_id=kakao_id)
                login(request, user)

                # JWT 토큰 생성
                payload = {'kakao_id': kakao_id}
                jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                print(jwt_token)
                return Response(status=status.HTTP_200_OK, data={'is_member': True, 'kakao_jwt': jwt_token})
            except User.DoesNotExist:
                return Response(status=status.HTTP_200_OK, data={'is_member': False})



            # user = User.objects.filter(kakao_id=kakao_id).first()
            # if user:
            #     login(request, user)
            #     # JWT 토큰 생성
            #     payload = {'kakao_id': kakao_id}
            #     jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            #     print(jwt_token)
            #     return Response(status=status.HTTP_200_OK, data={'is_member': True, 'kakao_jwt': jwt_token})
            # else:
            #     return Response(status=status.HTTP_200_OK, data={'is_member': False})
            
                # email = request.data.get("email")
                # print(email)

                # if not email:
                #     return Response(
                #         {"error": "Authorization code는 필수입니다."}, 
                #         status=status.HTTP_400_BAD_REQUEST
                #     )

                # user, created = User.objects.get_or_create(
                # kakao_id=kakao_id,
                # defaults={
                #     'username': profile.get("nickname"),
                #     'name': profile.get("nickname"),
                #     'avatar': profile.get("profile_image_url"),
                #     'kakao_id': kakao_id,
                #     'email' : email
                #     }
                # )

                # if not created:
                #     user.kakao_id = kakao_id
                #     user.save()

                # user.set_unusable_password()
                # user.save()
                # login(request, user)

                # payload = {'kakao_id': kakao_id}
                # jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                # return Response(status=status.HTTP_200_OK, data={'signup': True, 'kakao_jwt': jwt_token})

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)




class KakaoSignup(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            email = request.data.get("email")
            if not code or not email:
                return Response(
                    {"error": "Authorization code와 이메일은 필수입니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 세션에서 profile과 kakao_id 가져오기
            get_code = request.session.get('code')
            profile = request.session.get('kakao_profile')
            kakao_id = request.session.get('kakao_id')

            print(profile)
            print(code == get_code)
            print(code)
            print(get_code)

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

            payload = {'kakao_id': kakao_id}
            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return Response(status=status.HTTP_200_OK, data={'signup': True, 'kakao_jwt': jwt_token})
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





# class KakaoSignup(APIView):
#     def post(self, request):
#         try:
#             code = request.data.get("code")
#             email = request.data.get("email")
#             print(code, email)
#             print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")


#             if not code or not email:
#                 return Response(
#                     {"error": "Authorization code와 이메일은 필수입니다."}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             access_token_response = requests.post(
#                 "https://kauth.kakao.com/oauth/token",
#                 headers={"Content-Type": "application/x-www-form-urlencoded"},
#                 data={
#                     "grant_type": "authorization_code",
#                     "client_id": "583f1ebb47209c90313ca9808363f605",
#                     "redirect_uri": "http://127.0.0.1:3000/social/kakao",
#                     "code": code,
#                 },
#             )

#             if access_token_response.status_code != 200:
#                 return Response(
#                     access_token_response.json(), 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             print(access_token_response.json(), "\n")

#             access_token = access_token_response.json().get("access_token")
#             print(f"access_token: {access_token}")
#             print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#             refresh_token = access_token_response.json().get("refresh_token")
#             print(f"refresh_token: {refresh_token}")

#             if not access_token or not refresh_token:
#                 return Response(
#                     {"error": "Access token 또는 Refresh token을 가져올 수 없습니다."}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             user_data_response = requests.get(
#                 "https://kapi.kakao.com/v2/user/me",
#                 headers={
#                     "Authorization": f"Bearer {access_token}",
#                     "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
#                 }
#             )

#             if user_data_response.status_code != 200:
#                 return Response(
#                     user_data_response.json(), 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             user_data = user_data_response.json()
#             print(user_data, "\n")

#             kakao_account = user_data.get("kakao_account")
#             profile = kakao_account.get("profile")
#             kakao_id = user_data.get("id")

#             user, created = User.objects.get_or_create(
#                 kakao_id=kakao_id,
#                 defaults={
#                     'username': profile.get("nickname"),
#                     'name': profile.get("nickname"),
#                     'avatar': profile.get("profile_image_url"),
#                     'kakao_id': kakao_id,
#                     'email' : email,
#                     'refresh_token': refresh_token,
#                 }
#             )

#             if not created:
#                 user.kakao_id = kakao_id
#                 user.refresh_token = refresh_token
#                 user.save()

#             user.set_unusable_password()
#             user.save()
#             login(request, user)

#             payload = {'kakao_id': kakao_id}
#             jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

#             return Response(status=status.HTTP_200_OK, data={'signup': True, 'kakao_jwt': jwt_token})
            
#         except Exception as e:
#             print(e)
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)








        # def refreshToken(refresh_token):
            #     REST_API_KEY = "583f1ebb47209c90313ca9808363f605"
            #     REDIRECT_URI = "https://kauth.kakao.com/oauth/token"

            #     data = {
            #         "grant_type": "refresh_token",
            #         "client_id":f"{REST_API_KEY}",
            #         "refresh_token": refresh_token
            #     }    
            
            #     resp = requests.post(REDIRECT_URI , data=data)
            #     new_token = resp.json()

            #     return new_token['access_token']

        # print(refreshToken(refresh_token))