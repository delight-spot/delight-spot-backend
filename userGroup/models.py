# userGroups/models.py
from django.db import models
from common.models import CommonModel
# from django.contrib.auth.models import User
from django.conf import settings

class Group(CommonModel):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="my_groups",
    )
    def __str__(self):
        return self.name


class SharedList(CommonModel):
    group = models.ForeignKey("userGroup.Group", on_delete=models.CASCADE, null=True, blank=True, related_name="group",)
    store = models.ManyToManyField(
        "stores.Store",
        related_name="share_list",
    )

    def __str__(self):
        return self.group.name if self.group else 'No Group'
