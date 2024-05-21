from django.db import models


# 데이터베이스에 추가하지 않는 model -> 다른 model에서 재사용하기 위한 model
class CommonModel(models.Model):
    """Common Model Definition"""

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # 필드의 값을 해당 object가 생성될 때 시간으로 설정
    updated_at = models.DateTimeField(
        auto_now=True
    )  # object가 저장될 때마다 해당 필드를 현재 date로 설정

    # DB에 테이블을 만들지 않기 위한 코드
    # Django에서 model을 configure할 때 사용
    class Meta:
        abstract = True  # 데이터베이스에 저장하지 않는다.
