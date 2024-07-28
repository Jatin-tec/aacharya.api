from django.contrib import admin
from authentication.models import User, WatchHistory

admin.site.register(User)
admin.site.register(WatchHistory)