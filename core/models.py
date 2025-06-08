from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


# === User Model ===
class User(AbstractUser):
    display_name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    online_status = models.CharField(max_length=10, default="offline")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.username


# === Server Model ===
class Server(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_servers"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to="server_icons/", blank=True, null=True)

    def __str__(self):
        return self.name


# === Channel Model ===
class Channel(models.Model):
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="channels"
    )
    name = models.CharField(max_length=100)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name} - {self.name}"


# === Message Model ===
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.channel}"


# === Role Model ===
class Role(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict)  # JSON for flexibility
    color = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return f"{self.name} - {self.server.name}"
