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

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

import logging
logger = logging.getLogger(__name__)

app_name = "core"

urlpatterns = [
    path("servers/", views.server_list, name="server_list"),
    path("servers/join/<str:code>/", views.join_server, name="join_server"),
    path('servers/create/', views.create_server, name='create_server'),
    path('servers/discover/', views.discover_community_servers, name='discover_community'),
    path("servers/<uuid:server_id>/", views.server_detail, name="server_detail"),
    path('servers/<uuid:server_id>/roles/', views.roles_list, name='roles_list'),
    path('servers/<uuid:server_id>/roles/create/', views.create_role, name='create_role'),
    path('servers/<uuid:server_id>/roles/<uuid:role_id>/edit/', views.edit_role, name='edit_role'),
    path('servers/<uuid:server_id>/roles/<uuid:role_id>/assign/', views.assign_role, name='assign_role'),
    path('servers/<uuid:server_id>/create_channel/', views.create_channel, name='create_channel'),
    path('servers/<uuid:server_id>/create_category/', views.create_category, name='create_category'),
    path('servers/<uuid:server_id>/settings/', views.server_settings, name='server_settings'),
    path("servers/<uuid:server_id>/<uuid:category_id>/", views.category_detail, name="category_detail",),
    path('servers/<uuid:server_id>/<uuid:category_id>/create_channel/', views.create_channel, name='create_channel'),
    path("servers/<uuid:server_id>/<uuid:category_id>/<uuid:channel_id>/", views.channel_detail,name="channel_detail",),
    path("servers/<uuid:server_id>/<uuid:category_id>/<uuid:channel_id>/<uuid:message_id>/edit/", views.edit_message, name="edit_message"),
    path("servers/<uuid:server_id>/<uuid:category_id>/<uuid:channel_id>/<uuid:message_id>/delete/", views.delete_message, name="delete_message"),
    path('servers/<uuid:server_id>/<uuid:category_id>/<uuid:channel_id>/<uuid:message_id>/history/', views.message_history, name='message_history',),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<uuid:user_id>/", views.profile, name="profile"),
    path("profile/<uuid:user_id>/send_request/", views.send_friend_request, name="send_friend_request"),
    path("profile/<uuid:user_id>/requests/", views.friend_requests, name="friend_requests"),
    path("profile/<uuid:user_id>/friends/", views.friends_list, name="friends_list"),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='core/auth/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='core/auth/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/auth/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='core/auth/password_reset_done.html'), name='password_reset_complete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
