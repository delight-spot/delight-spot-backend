from django.urls import path
from . import views

urlpatterns = [
    path("bookings", views.Bookings.as_view()),
    # path("bookings/stores/<int:store_pk>", views.BookingToggle.as_view()),
    # path("/<int:pk>/stores/<int:store_pk>", views.BookingToggle.as_view()),
]