from django.db import models
from common.models import CommonModel
from django.conf import settings

class Notice(CommonModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name="notice",
    )
    name = models.TextField()
    description = models.TextField()
    top_fixed = models.BooleanField(verbose_name='fix', default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-id'] # 정렬기준 최신순(늦게 작성된 글이 최신글임)
    