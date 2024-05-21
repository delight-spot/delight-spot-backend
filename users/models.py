from django.db import models
from django.contrib.auth.models import AbstractUser


# user을 조작할 수 있는 class
class User(AbstractUser):

    class GenderChoices(models.TextChoices):
        MALE = (
            "male",
            "Male",
        )  # database에 들어갈 value, 관리자 페이지에서 보게 될 label이 들어간다.
        FEMALE = ("female", "Female")

    avatar = models.URLField(blank=True)  # form에서 필드가 필수적이지 않게 해준다.
    name = models.CharField(max_length=150, default="")
    is_host = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
