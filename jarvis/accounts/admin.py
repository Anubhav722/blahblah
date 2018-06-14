# Django Imports
from django.contrib import admin

# App Imports
from .models import Client, UserProfile


class ClientAdmin(admin.ModelAdmin):
    list_filter = ('organization',)
    list_display = ('key', 'organization')


class UserProfileAdmin(admin.ModelAdmin):
    list_filter = ('user',)
    list_display = ('client', 'user', 'limit', 'label')


admin.site.register(Client, ClientAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
