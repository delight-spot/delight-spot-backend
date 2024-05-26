from django.contrib import admin
from .models import Reviews
from django.db.models import Avg
from django.db import models

# class ScoreFilter(admin.SimpleListFilter):
#     title = "평점으로 보기"
#     parameter_name = "rating"

#     def lookups(self, request, model_admin):
#         return [
#             ("1_1.9", "1.0 ~ 1.9점"),
#             ("2_2.9", "2.0 ~ 2.9점"),
#             ("3_3.9", "3.0 ~ 3.9점"),
#             ("4_4.9", "4.0 ~ 4.9점"),
#             ("5", "5점"),
#         ]

#     def queryset(self, request, queryset):
#         rate = self.value()
#         if rate == "1_1.9":
#             return queryset.filter(total_rating__gte=1, total_rating__lte=1.9)
#         elif rate == "2_2.9":
#             return queryset.filter(total_rating__gte=2, total_rating__lte=2.9)
#         elif rate == "3_3.9":
#             return queryset.filter(total_rating__gte=3, total_rating__lte=3.9)
#         elif rate == "4_4.9":
#             return queryset.filter(total_rating__gte=4, total_rating__lte=4.9)
#         elif rate == "5":
#             return queryset.filter(total_rating=5)
#         else:
#             return queryset

@admin.register(Reviews)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",  # models.py 에서 설정한 str 메서드를 보여준다.
        "total_rating",
        "taste_rating",
        "atmosphere_rating",
        "kindness_rating",
        "clean_rating",
        "parking_rating",
        "restroom_rating",
        "store",
    )
    search_fields = (
        "store",
    )
    # list_filter = (
    #     # ScoreFilter,

    # )
    
    # @property
    # def total_rating(self, obj):
    #     return obj.get_total_rating()  # `get_total_rating()` 메서드 사용

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.annotate(total_rating=Avg(
    #         models.Case(
    #             models.When(taste_rating__isnull=False, then='taste_rating'),
    #             models.When(atmosphere_rating__isnull=False, then='atmosphere_rating'),
    #             models.When(kindness_rating__isnull=False, then='kindness_rating'),
    #             models.When(clean_rating__isnull=False, then='clean_rating'),
    #             models.When(parking_rating__isnull=False, then='parking_rating'),
    #             models.When(restroom_rating__isnull=False, then='restroom_rating'),
    #         )
    #     ))