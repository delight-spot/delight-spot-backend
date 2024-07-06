from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg       import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Delight Spot",
      default_version='v1',
      description="사용자들이 맛집(음식점, 카페) 또는 기타 즐거운 장소를 공유",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="jangth0056@gmail.com"),
      license=openapi.License(name="mit"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path('admin/', admin.site.urls),
    # path('stores/', include('stores.urls')),
    path('api/v1/', include("stores.urls")),
    path('api/v1/', include("bookings.urls")),
    path('api/v1/', include("users.urls")),
    path('api/v1/', include("userGroup.urls")),
    path('api/v1/', include("notice.urls")),
] 
