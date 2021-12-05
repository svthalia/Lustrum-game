from django.contrib import admin

from .models import Player
from .models import Murder
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'profilePicture')
    search_fields = ['name']


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'target', "isDead")
    search_fields = ['user']


admin.site.register(User, UserAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Murder)
