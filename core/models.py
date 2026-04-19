from datetime import date
from calendar import monthrange

from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db import models
import uuid, random, secrets

# Create your models here.

SERVER_ICON_CHOICES = [
    "/media/server_icons/server-default-1.png",
    "/media/server_icons/server-default-2.png",
    "/media/server_icons/server-default-3.png",
]

USER_ICON_CHOICES = [
    "/media/avatars/user-default-1.png",
    "/media/avatars/user-default-2.png",
    "/media/avatars/user-default-3.png",
]

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

    # === Age / Parental Controls ===
    class MinorBirthdatePrecision(models.TextChoices):
        AGE_RANGE = "age_range", "Age range"
        AGE_YEARS = "age_years", "Age"
        MONTH_YEAR = "month_year", "MM/YYYY"
        FULL_DATE = "full_date", "DD/MM/YYYY"

    class MinorAgeRange(models.TextChoices):
        UNDER_13 = "under_13", "Under 13"
        BETWEEN_13_AND_15 = "13_15", "13-15"
        BETWEEN_16_AND_17 = "16_17", "16-17"

    date_of_birth = models.DateField(blank=True, null=True)
    is_minor_account = models.BooleanField(default=False)
    parental_controls_enabled = models.BooleanField(default=False)
    guardian_email = models.EmailField(blank=True)
    guardian_email_verified_at = models.DateTimeField(null=True, blank=True)
    minor_birthdate_precision = models.CharField(max_length=24, choices=MinorBirthdatePrecision.choices, blank=True)
    minor_age_range = models.CharField(max_length=24, choices=MinorAgeRange.choices, blank=True)
    minor_age_years = models.PositiveSmallIntegerField(null=True, blank=True)
    minor_age_recorded_at = models.DateTimeField(null=True, blank=True)
    minor_birth_year = models.PositiveSmallIntegerField(null=True, blank=True)
    minor_birth_month = models.PositiveSmallIntegerField(null=True, blank=True)
    minor_birth_day = models.PositiveSmallIntegerField(null=True, blank=True)
    guardian_allows_nsfw = models.BooleanField(default=False)
    guardian_allows_16plus = models.BooleanField(default=False)
    guardian_locks_profile = models.BooleanField(default=False)
    guardian_restrict_dms = models.BooleanField(default=False)

    def shared_servers_with(self, other_user):
        return self.servers.filter(id__in=other_user.servers.all())

    def shared_friends_with(self, other_user):
        return self.friends.filter(id__in=other_user.friends.all())

    @property
    def guardian_email_verified(self):
        return bool(self.guardian_email and self.guardian_email_verified_at)

    def get_effective_age(self):
        if not self.is_minor_account:
            return None
        now = timezone.localdate()
        if self.minor_birthdate_precision == self.MinorBirthdatePrecision.AGE_RANGE:
            mapping = {
                self.MinorAgeRange.UNDER_13: 12,
                self.MinorAgeRange.BETWEEN_13_AND_15: 15,
                self.MinorAgeRange.BETWEEN_16_AND_17: 17,
            }
            return mapping.get(self.minor_age_range)
        if self.minor_birthdate_precision == self.MinorBirthdatePrecision.AGE_YEARS:
            if self.minor_age_years is None or self.minor_age_recorded_at is None:
                return None
            days_elapsed = max(0, (timezone.now() - self.minor_age_recorded_at).days)
            return self.minor_age_years + (days_elapsed // 365)
        if self.minor_birthdate_precision == self.MinorBirthdatePrecision.MONTH_YEAR:
            if not self.minor_birth_year or not self.minor_birth_month:
                return None
            from calendar import monthrange
            last_day = monthrange(self.minor_birth_year, self.minor_birth_month)[1]
            birthdate = date(self.minor_birth_year, self.minor_birth_month, last_day)
        elif self.minor_birthdate_precision == self.MinorBirthdatePrecision.FULL_DATE:
            if not (self.minor_birth_year and self.minor_birth_month and self.minor_birth_day):
                return None
            birthdate = date(self.minor_birth_year, self.minor_birth_month, self.minor_birth_day)
        else:
            return None
        age = now.year - birthdate.year - ((now.month, now.day) < (birthdate.month, birthdate.day))
        return max(age, 0)

    def allows_nsfw_content(self):
        if not self.is_minor_account:
            return True
        age = self.get_effective_age()
        if age is not None and age >= 18:
            return True
        return bool(self.guardian_allows_nsfw)

    def allows_16plus_content(self):
        if not self.is_minor_account:
            return True
        age = self.get_effective_age()
        if age is not None and age >= 16:
            return True
        return bool(self.guardian_allows_16plus)

    def __str__(self):
        return self.display_name or self.username

    @property
    def avatar_or_random(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return random.choice(USER_ICON_CHOICES)


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

    @property
    def icon_or_random(self):
        if self.icon and hasattr(self.icon, "url"):
            return self.icon.url
        return random.choice(SERVER_ICON_CHOICES)


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


# === Guardian Email Verification ===
class GuardianEmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guardian_tokens")
    guardian_email = models.EmailField()
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["token"]), models.Index(fields=["expires_at"])]

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_usable(self):
        return self.used_at is None and not self.is_expired

    def __str__(self):
        return f"GuardianToken for {self.user.username}"
