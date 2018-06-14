

# App Imports
from jarvis.core.models import BaseModel
from .constants import DEFAULT_ALLOWED_LIMIT_COUNT
from .generators import (
    generate_client_key, generate_client_secret
)

# Django Imports
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Client(BaseModel):
    """
    Model to store client related information

    Fields:
    * :attr: `client_key` Client Key
    * :attr: `client_secret` Client Secret
    * :attr: `organization` Organization from where client belongs to
    """
    key = models.CharField(
        max_length=255, default=generate_client_key, help_text='Client Key'
    )
    secret = models.CharField(
        max_length=255, default=generate_client_secret, help_text='Client Secret'
    )
    organization = models.CharField(
        max_length=50, unique=True, help_text='Organization Name'
    )

    class Meta:
        ordering = ('-created_date', )

    def __str__(self):
        return "%s" % self.organization


@python_2_unicode_compatible
class UserProfile(BaseModel):

    """
    UserProfile model to store extra information for the user of the system

    Fields:
    * :attr: `client` ref to Client
    * :attr: `user` The Django user
    * :attr: `limit` Allowed limit
    * :attr: `label` To Identify user with label
    """
    client = models.ForeignKey(Client, null=True, related_name='profiles')
    user = models.OneToOneField(User, related_name='profile')
    limit = models.PositiveIntegerField(
        default=DEFAULT_ALLOWED_LIMIT_COUNT, help_text='Access Limit'
    )
    label = models.CharField(max_length=50, help_text='User Profile Label')

    class Meta:
        ordering = ('-created_date', )

    def __str__(self):
        return "%s" % self.user.username
