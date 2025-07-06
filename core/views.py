from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Server, Channel, Message, User, FriendRequest, Category, MessageEditHistory, Role
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, ProfileEditForm, ServerSettingsForm
from django.http import HttpResponseForbidden
import uuid
from django.core.exceptions import ValidationError, PermissionDenied
import logging
from django import forms
from django.utils import timezone
logger = logging.getLogger(__name__)

# Create your views here.


def home(request):
    return render(request, "home.html")


@login_required
def server_list(request):
    # servers = Server.objects.all()
    servers = request.user.servers.all()  # Only servers the user is a member of
    return render(request, "core/server/servers.html", {"servers": servers})


@login_required
def discover_community_servers(request):
    servers = Server.objects.filter(community=True).exclude(members=request.user)
    return render(request, "core/server/discover_community.html", {"servers": servers})


@login_required
def server_detail(request, server_id):
    server = get_object_or_404(Server, id=server_id)
    # Check if user is a member or if community=True
    if not server.community and request.user not in server.members.all():
        return PermissionDenied("You do not have access to this server.")
    categories = server.categories.prefetch_related("channels").all()
    user_roles = server.roles.filter(users=request.user)
    channels = server.channels.filter(allowed_roles__in=user_roles).distinct()
    user = request.user

    if request.method == "POST" and user in server.members.all():
        # Use the first channel as default for sending
        channel = channels.first()
        Message.objects.create(
            sender=user, channel=channel, content=request.POST["content"]
        )

    return render(
        request,
        "core/server/server_detail.html",
        {
            "server": server,
            "categories": categories,
            "channels": channels,  # Optional: if you want to show non-categorized channels separately
        },
    )


@login_required
def join_server(request, code):
    server = get_object_or_404(Server, join_code=code)
    server.members.add(request.user)
    everyone_role = server.roles.get(name="@everyone")
    everyone_role.users.add(request.user)
    return redirect("core:server_detail", server_id=server.id)


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect("core:profile", user_id=to_user.id)


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user
    )
    friend_request.status = "accepted"
    friend_request.save()
    request.user.friends.add(friend_request.from_user)
    friend_request.from_user.friends.add(request.user)
    return redirect("core:profile", user_id=friend_request.from_user.id)


@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user
    )
    friend_request.delete()
    return redirect("core:profile", user_id=friend_request.from_user.id)


@login_required
def profile(request, **kwargs):
    user_id = kwargs.get("user_id")
    if user_id:
        try:
            # Validate UUID first!
            uuid_obj = uuid.UUID(user_id, version=4)
            user_profile = User.objects.get(id=uuid_obj)
        except (ValueError, ValidationError, User.DoesNotExist):
            return render(request, "core/errors/user_not_found.html", status=404)
    else:
        user_profile = request.user

    shared_servers = request.user.shared_servers_with(user_profile)
    shared_friends = request.user.shared_friends_with(user_profile)
    friend_requests = FriendRequest.objects.filter(
        to_user=request.user, status="pending"
    )

    return render(
        request,
        "core/profile/profile.html",
        {
            "user_profile": user_profile,
            "shared_servers": shared_servers,
            "shared_friends": shared_friends,
            "friend_requests": friend_requests,
        },
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("core:profile")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "core/profile/edit_profile.html", {"form": form})


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            user.email = form.cleaned_data.get("email")
            user.display_name = form.cleaned_data.get("display_name")
            user.bio = form.cleaned_data.get("bio")
            if form.cleaned_data.get("avatar"):
                user.avatar = form.cleaned_data.get("avatar")
            user.save()

            from django.contrib.auth import login

            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})


def theme_preview(request):
    themes = ["dark", "light", "orange", "synth"]
    return render(request, "themes/preview.html", {"themes": themes})


class ServerCreationForm(forms.ModelForm):
    community = forms.BooleanField(required=False, initial=False, label="Public (Community Server)?")

    class Meta:
        model = Server
        fields = ["name", "description", "icon", "community"]


@login_required
def create_server(request):
    if request.method == "POST":
        form = ServerCreationForm(request.POST, request.FILES)
        if form.is_valid():
            server = form.save(commit=False)
            server.owner = request.user
            server.save()
            server.members.add(request.user)  # Add owner as first member

            # Create default category
            uncategorized = Category.objects.create(server=server, name="Uncategorized", protected=True)

            # Create default "general" channel
            Channel.objects.create(
                server=server,
                name="general",
                channel_type="text",
                category=uncategorized,
            )

            return redirect("core:server_detail", server_id=server.id)
    else:
        form = ServerCreationForm()
    return render(request, "core/server/create_server.html", {"form": form})


class CategoryCreationForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


@login_required
def create_category(request, server_id):
    server = get_object_or_404(Server, id=server_id, owner=request.user)
    if request.method == "POST":
        form = CategoryCreationForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.server = server
            category.save()
            return redirect("core:server_detail", server_id=server.id)
    else:
        form = CategoryCreationForm()
    return render(request, "core/server/category/create_category.html", {"form": form, "server": server})


class ChannelCreationForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ["name", "channel_type", "category"]


@login_required
def create_channel(request, server_id, category_id=None):
    server = get_object_or_404(Server, id=server_id, owner=request.user)

    if request.method == "POST":
        # Use manual fields instead of the Django form
        name = request.POST.get("name")
        category_id = request.POST.get("category_id")
        channel_type = request.POST.get("channel_type")
        category = Category.objects.filter(id=category_id, server=server).first()

        Channel.objects.create(
            name=name,
            server=server,
            category=category,  # might be None if no category chosen
            channel_type=channel_type,
        )
        return redirect("core:server_detail", server_id=server.id)

    # Load categories for dropdown
    categories = server.categories.all()
    return render(request, "core/server/category/channel/create_channel.html", {"server": server, "categories": categories, "selected_category": category_id})


@login_required
def channel_detail(request, server_id, category_id, channel_id):
    server = get_object_or_404(Server, id=server_id)
    category = get_object_or_404(Category, id=category_id, server=server)
    channel = get_object_or_404(
        Channel, id=channel_id, server=server, category=category
    )

    if request.method == "POST" and request.user in server.members.all():
        Message.objects.create(
            sender=request.user, channel=channel, content=request.POST["content"]
        )
        return redirect(
            "core:channel_detail",
            server_id=server.id,
            category_id=category.id,
            channel_id=channel.id,
        )

    messages = channel.messages.order_by("created_at")
    return render(
        request,
        "core/server/category/channel/channel_detail.html",
        {
            "server": server,
            "category": category,
            "channel": channel,
            "messages": messages,
            "user": request.user,
        },
    )


@login_required
def category_detail(request, server_id, category_id):
    server = get_object_or_404(Server, id=server_id)
    category = get_object_or_404(Category, id=category_id, server=server)

    # Optional: show only channels the user can access
    channels = category.channels.all()

    return render(
        request,
        "core/server/category/category_detail.html",
        {
            "server": server,
            "category": category,
            "channels": channels,
        },
    )


@login_required
def edit_message(request, server_id, category_id, channel_id, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)

    if request.method == "POST":
        new_content = request.POST.get("content")

        # Save edit history
        MessageEditHistory.objects.create(
            message=message, editor=request.user, old_content=message.content
        )

        # Update the message
        message.content = new_content
        message.edited_at = timezone.now()
        message.save()

        return redirect(
            "core:channel_detail",
            server_id=message.channel.server.id,
            category_id=message.channel.category.id,
            channel_id=message.channel.id,
        )

    return render(request, "core/server/category/channel/message/edit_message.html", {"message": message})


@login_required
def message_history(request, server_id, category_id, channel_id, message_id):
    server = get_object_or_404(Server, id=server_id)
    category = get_object_or_404(Category, id=category_id, server=server)
    channel = get_object_or_404(
        Channel, id=channel_id, server=server, category=category
    )
    message = get_object_or_404(Message, id=message_id, channel=channel)

    history = message.edit_history.all().order_by("-edited_at")

    return render(
        request,
        "core/server/category/channel/message/message_history.html",
        {
            "server": server,
            "category": category,
            "channel": channel,
            "message": message,
            "history": history,
        },
    )


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)

    # Soft delete: mark as deleted, keep in DB
    message.deleted = True
    message.save()

    return redirect(
        "core:channel_detail",
        server_id=message.channel.server.id,
        category_id=message.channel.category.id,
        channel_id=message.channel.id,
    )


@login_required
def roles_list(request, server_id):
    server = get_object_or_404(Server, id=server_id, owner=request.user)
    roles = server.roles.all()
    return render(request, "core/server/role/roles_list.html", {"server": server, "roles": roles})


@login_required
def delete_category(request, server_id, category_id):
    server = get_object_or_404(Server, id=server_id, owner=request.user)
    category = get_object_or_404(Category, id=category_id, server=server)

    if category.protected:
        return HttpResponseForbidden("This category cannot be deleted.")

    category.delete()
    return redirect("core:server_detail", server_id=server.id)


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "color"]  # Add other fields as needed


@login_required
def create_role(request, server_id):
    server = get_object_or_404(Server, id=server_id, owner=request.user)

    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.server = server
            role.save()
            return redirect("core:roles_list", server_id=server.id)
    else:
        form = RoleForm()

    return render(request, "core/server/role/create_role.html", {"form": form, "server": server})


@login_required
def edit_role(request, server_id, role_id):
    server = get_object_or_404(Server, id=server_id, owner=request.user)
    role = get_object_or_404(Role, id=role_id, server=server)

    if request.method == "POST":
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect("core:roles_list", server_id=server.id)
    else:
        form = RoleForm(instance=role)

    return render(
        request, "core/server/role/edit_role.html", {"form": form, "role": role, "server": server}
    )


@login_required
def assign_role(request, server_id, role_id):
    server = get_object_or_404(Server, id=server_id, owner=request.user)
    role = get_object_or_404(Role, id=role_id, server=server)
    members = server.members.all()

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = get_object_or_404(User, id=user_id)

        # Example: assume you have a ManyToMany on User or a through table
        user.roles.add(role)  # If you have a ManyToManyField
        return redirect("core:roles_list", server_id=server.id)

    return render(
        request,
        "core/server/role/assign_role.html",
        {"server": server, "role": role, "members": members},
    )


@login_required
def friend_requests(request, user_id):
    requests = FriendRequest.objects.filter(to_user=request.user, status="pending")
    return render(request, "core/profile/friend_requests.html", {"requests": requests})


@login_required
def friends_list(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    return render(request, "core/profile/friends_list.html", {"friends": profile_user.friends.all()})


@login_required
def server_settings(request, server_id):
    server = get_object_or_404(Server, id=server_id, owner=request.user)

    if request.method == "POST":
        form = ServerSettingsForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            return redirect("core:server_detail", server_id=server.id)
    else:
        form = ServerSettingsForm(instance=server)

    return render(
        request, "core/server/server_settings.html", {"server": server, "form": form}
    )
