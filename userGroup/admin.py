# userGroups/admin.py
from django.contrib import admin
from .models import Group, SharedList

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(SharedList)
class SharedListAdmin(admin.ModelAdmin):
    list_display = ('group', "created_at",)

