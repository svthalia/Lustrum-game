from django.contrib import admin

from .models import Player
from .models import Murder
from .models import User

admin.site.register(User)
admin.site.register(Player)
admin.site.register(Murder)

