from django.contrib import admin

from .models import RemoteUser

class RemoteUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'remote_username')
    model = RemoteUser
admin.site.register(RemoteUser, RemoteUserAdmin)
