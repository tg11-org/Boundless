from django.contrib import admin
from .models import User, Server, Channel, Message, Role

# Register your models here.

admin.site.register(User)
admin.site.register(Server)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(Role)
