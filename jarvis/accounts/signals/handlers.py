# Django Imports
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save

# DRF Imports
from rest_framework.authtoken.models import Token

# App Imports
from ..models import Client, UserProfile
from ..generators import (
    generate_client_key, generate_client_secret
)

@receiver(
    signal=pre_save, sender=Client,
    dispatch_uid='client-key-and-client-secret-creation-signal'
)
def create_client_key_and_secret(sender, instance, created=False, **kwargs):
    """
    Create Client Key and Client Secret for particular organization
    """
    if created:
        # Generate Client Key
        client_key = generate_client_key()
        while Client.objects.filter(key=client_key).exists():  # Sanity Check
            client_key = generate_client_key()

        # Generate Client Secret
        client_secret = generate_client_secret()
        while Client.objects.filter(secret=client_secret).exists():  # Sanity Check
            client_secret = generate_client_secret()

        instance.key = client_key
        instance.secret = client_secret

@receiver(signal=post_save, sender=User, dispatch_uid='user-access-token-creation-signal')
def create_access_token_for_user(sender, instance, created=False, **kwargs):
    """
    Automatically create access_token for user whenever user object is created
    """
    if created:
        try:
            Token.objects.create(user=instance)
        except Token.DoesNotExist:
            return None

@receiver(signal=post_save, sender=User, dispatch_uid='user-profile-creation-signal')
def create_user_profile(sender, instance, created=False, **kwargs):
    """
    A receiver callback function for User model's post save method.
    """
    if created:
        try:
            user_profile, created = UserProfile.objects.get_or_create(user=instance)
        except UserProfile.DoesNotExist:
            return None
