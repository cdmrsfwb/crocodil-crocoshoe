from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Player)


class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'player'


class UserAdmin(BaseUserAdmin):
    inlines = (PlayerInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
