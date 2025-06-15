# Copyright (C) 2025 TG11
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Server

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    display_name = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    avatar = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "email",
            "display_name",
            "bio",
            "avatar",
        )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "display_name",
            "first_name",
            "last_name",
            "email",
            "bio",
            "avatar",
            "phone_number",
            "show_email",
            "show_legal_name",
            "show_phone_number",
            "show_bio",
            "show_avatar",
        ]


class ServerSettingsForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ["name", "description", "community", "icon"]
