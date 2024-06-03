from django.urls import path
from . import views

urlpatterns = [
    path('notices', views.NoticeViews.as_view()),
]