from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.db import models
import uuid

# Create your models here.


# === User Model ===
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    online_status = models.CharField(max_length=10, default="offline")
    created_at = models.DateTimeField(auto_now_add=True)
    friends = models.ManyToManyField("self", blank=True)
    phone_number = PhoneNumberField(blank=True, null=True)

    show_email = models.BooleanField(default=False)
    show_legal_name = models.BooleanField(default=False)
    show_phone_number = models.BooleanField(default=False)
    show_bio = models.BooleanField(default=True)
    show_avatar = models.BooleanField(default=True)

    def shared_servers_with(self, other_user):
        return self.servers.filter(id__in=other_user.servers.all())

    def shared_friends_with(self, other_user):
        return self.friends.filter(id__in=other_user.friends.all())

    def __str__(self):
        return self.display_name or self.username


class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_friend_requests"
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_friend_requests"
    )
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("accepted", "Accepted")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)


# === Server Model ===
def generate_join_code():
    return uuid.uuid4()

class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_servers"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to="server_icons/", blank=True, null=True)
    community = models.BooleanField(default=False)
    join_code = models.CharField(max_length=72, unique=True, default=generate_join_code)
    members = models.ManyToManyField(User, related_name="servers", blank=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            Role.objects.create(server=self, name="@everyone")

    def get_join_link(self):
        return f"/servers/join/{self.join_code}/"

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    protected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (in {self.server.name})"


# === Role Model ===
class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict)  # JSON for flexibility
    users = models.ManyToManyField(User, related_name="roles", blank=True)
    color = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return f"{self.name} - {self.server.name}"


# === Channel Model ===
class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TEXT = 'text'
    VOICE = 'voice'
    VIDEO = 'video'
    MEDIA = 'media'
    FORUM = 'forum'
    ANNOUNCEMENT = 'announcement'
    EVENT = 'event'
    SUPPORT = 'support'
    TICKET = 'ticket'
    TYPE_CHOICES = [
        (TEXT, "Text"),
        (VOICE, "Voice"),
        (VIDEO, "Video"),
        (MEDIA, "Media"),
        (FORUM, "Forum"),
        (ANNOUNCEMENT, "Announcement"),
        (EVENT, "Event"),
        (SUPPORT, "Support"),
        (TICKET, "Ticket"),
    ]
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="channels"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="channels",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=32, choices=TYPE_CHOICES, default=TEXT)
    allowed_roles = models.ManyToManyField(Role, related_name="channels", blank=True)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name} - {self.name}"


# === Message Model ===
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.channel}"


class MessageEditHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="edit_history"
    )
    editor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )  # Who edited it
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)  # When this edit happened

    def __str__(self):
        return f"MessageEditHistory from {self.sender} in {self.channel} by {self.editor} to {self.old_content}"


class GroupChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="group_chats")
    created_at = models.DateTimeField(auto_now_add=True)


class GroupChatMessage(models.Model):
    group = models.ForeignKey(
        GroupChat, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
