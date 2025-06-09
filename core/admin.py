from django.contrib import admin
from .models import User, Server, Category, Channel, Message, Role, MessageEditHistory

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "community", "created_at")
    search_fields = ("name", "owner__username")
    list_filter = ("community",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "server")
    search_fields = ("name", "server__name")


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "server", "category", "channel_type")
    search_fields = ("name", "server__name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "channel", "created_at", "edited_at", "deleted")
    search_fields = ("content", "sender__username")


@admin.register(MessageEditHistory)
class MessageEditHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "editor", "edited_at")
    search_fields = ("old_content", "editor__username")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "server", "color")
    search_fields = ("name", "server__name")
