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

import logging
logger = logging.getLogger(__name__)

urlpatterns = [
    path("servers/", views.server_list, name="server_list"),
    path("servers/join/<str:code>/", views.join_server, name="join_server"),
    path('servers/create/', views.create_server, name='create_server'),
    path("servers/<uuid:server_id>/", views.server_detail, name="server_detail"),
    path('servers/<uuid:server_id>/create_category/', views.create_category, name='create_category'),
    path("servers/<uuid:server_id>/<uuid:category_id>/",views.category_detail,name="category_detail",),
    path('servers/<uuid:server_id>/<uuid:category_id>/create_channel/', views.create_channel, name='create_channel'),
    path("servers/<uuid:server_id>/<uuid:category_id>/<uuid:channel_id>/",views.channel_detail,name="channel_detail",),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:user_id>/", views.profile, name="profile"),
]
