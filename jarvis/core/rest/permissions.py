# App Imports
from jarvis.accounts.models import Client, UserProfile

# Django Imports
from django.conf import settings

# DRF Imports
from rest_framework import permissions
from rest_framework.exceptions import APIException


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to active admin users.
    """

    def has_permission(self, request, view):
        client_key = request.META.get('HTTP_AIRCTO_CLIENT_KEY', None)
        client_secret = request.META.get('HTTP_AIRCTO_CLIENT_SECRET', None)

        try:
            assert (client_key and client_secret)
            client = Client.objects.get(key=client_key, secret=client_secret)
        except (AssertionError, Client.DoesNotExist):
            raise APIException({
                'status': 'Unauthorized',
                'message': 'Authentication values are incorrect/missing.',
            })

        request.client = client
        return request


class AllowInternalServiceOnly(permissions.BasePermission):
    """
    Allow access to only internal aircto services. i.e. `aircto-backend`
    """

    def has_permission(self, request, view):

        try:
            assert request.auth
        except AssertionError:
            raise APIException({
                'status': 'Unauthorized',
                'message': 'Authorization is required to perform this action.',
            })

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return APIException({
                'status': 'Failed',
                'message': 'User profile not found.',
            })

        try:
            user_organization = user_profile.client.organization
        except AttributeError:
            raise APIException({
                'status': 'Failed',
                'message': 'Cannot authenticate the user.',
            })

        if user_organization==settings.INTERNAL_RESUME_PARSER_USER:
            return True
        return False
