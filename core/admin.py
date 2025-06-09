from django.contrib import admin
from .models import User, Server, Channel, Message, Role, MessageEditHistory

# Register your models here.

admin.site.register(User)
admin.site.register(Server)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(Role)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "channel", "created_at", "edited_at", "content")
    search_fields = ("content", "sender__username")


@admin.register(MessageEditHistory)
class MessageEditHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "editor", "edited_at", "old_content")
    search_fields = ("old_content", "editor__username", "message__id")
