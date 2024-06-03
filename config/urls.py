from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),

    # path('stores/', include('stores.urls')),

    path('api/v1/', include("stores.urls")),
    path('api/v1/', include("medias.urls")),
    path('api/v1/', include("bookings.urls")),
    path('api/v1/', include("users.urls")),
    path('api/v1/', include("userGroup.urls")),
    path('api/v1/', include("notice.urls")),
] 
