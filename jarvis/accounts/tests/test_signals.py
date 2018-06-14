# App Imports
from ..models import Client, UserProfile
from .factories import UserFactory, UserProfileFactory, ClientFactory

# Django Imports
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# DRF Imports
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

# Miscellaneous
from faker import Faker

fake = Faker()
User = get_user_model()


class UserCreationTest(TestCase):
    """
    Test cases for post save signal

    ==================
    Expected Behaviour
    ==================
    After triggering post-save signal of User model:
        - It should create Token
        - It should create UserProfile
    """
    def setUp(self):
        self.user = UserFactory(username='test-user')

    def tearDown(self):
        del self.user

    def test_token_creation(self):
        self.assertTrue(self.user.auth_token.key)

    def test_user_profile_creation(self):
        self.assertTrue(self.user.profile)


class ClientKeySecretTests(TestCase):
    """
    Test cases for pre-save signal of Client

    ==================
    Expected Behaviour
    ==================
    It should generate `Client Key` and `Client Secret` values.
    """
    def setUp(self):
        self.client = ClientFactory()
        self.aircto_client = ClientFactory(organization='Aircto')

    def tearDown(self):
        del self.client
        del self.aircto_client

    def test_pre_save_signal_client_creation(self):
        self.assertTrue(self.aircto_client.key)
        self.assertTrue(self.aircto_client.secret)

    def test_client_key_secret_signals_triggered(self):
        key = self.client.key
        secret = self.client.secret
        # To check if after save() method client key and secret values are same.
        self.client.save()
        self.assertEqual(key, self.client.key)
        self.assertEqual(secret, self.client.secret)

class ClientCreateClientKeyAndSecret(TestCase):

    def test_create_client_key_and_secret(self):
        client = Client.objects.create(organization='Batman')

        self.assertEqual(len(client.key), 40)
        self.assertEqual(len(client.secret), 64)
        self.assertEqual(client, Client.objects.first())
        self.assertEqual(client.organization, 'Batman')

    def test_create_user_profile(self):
        user = User.objects.create_user(username='anubhav', password='password', email='anubhav@gmail.com')
        self.assertEqual(user.profile, UserProfile.objects.first())
        self.assertEqual(user.username, UserProfile.objects.first().user.username)