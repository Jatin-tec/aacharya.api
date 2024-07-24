from django.contrib import admin
from conversation.models import Video, Topic, Conversation, Note

admin.site.register(Video)
admin.site.register(Topic)
admin.site.register(Conversation)
admin.site.register(Note)