# App Imports
from .models import UserProfile
from .generators import generate_username

# DRF Imports
from rest_framework import serializers

# Django Imports
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    limit = serializers.IntegerField(source='profile.limit')
    label = serializers.CharField(source='profile.label')

    class Meta:
        model = User
        exclude = ('username', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        label = ''
        profile = validated_data.pop('profile', None)
        if profile:
            limit = profile.get('limit', None)
            label = profile.get('label', None)
        user = User.objects.create(username=generate_username())
        user.profile.limit = limit
        user.profile.label = label
        return user
