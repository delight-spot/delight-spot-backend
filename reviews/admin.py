from django.contrib import admin
from .models import Reviews


class ScoreFilter(admin.SimpleListFilter):
    title = "평점으로 보기"
    parameter_name = "score"

    def lookups(self, request, model_admin):  # 튜플의 리스트를 리턴해야 한다.
        return [
            ("1", "1점"),
            ("2", "2점"),
            ("3", "3점"),
            ("4", "4점"),
            ("5", "5점, Recomment"),
        ]

    def queryset(self, request, rating):
        # print(rating)
        rate = self.value()
        if rate is None:
            pass
        else:
            return rating.filter(
                rating__contains=rate,
            )

@admin.register(Reviews)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",  # models.py 에서 설정한 str 메서드를 보여준다.
        "rating",
        "description",
        "store",
    )
    list_filter = (
        ScoreFilter,
        "rating",
        "user__is_host",
    )
