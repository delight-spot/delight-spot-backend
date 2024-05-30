from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
    

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

    objects = UserManager()

    def __str__(self):
        return self.email