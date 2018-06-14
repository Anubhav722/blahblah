# App Imports
from ..views import UserView
from ..models import Client, UserProfile
from .factories import ClientFactory, UserFactory
from ..generators import generate_client_key, generate_client_secret

# Django Imports
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

# DRF Imports
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

# Miscellaneous
from faker import Faker

fake = Faker()
User = get_user_model()


class UserViewTests(TestCase):
    """
    Test cases for User View (Authentication)
    """
    def setUp(self):
        self.api_client = APIClient()
        self.client_obj = ClientFactory()
        self.factory = RequestFactory()
        self.user_profile_url = reverse('accounts:user-profile')
        self.data = {
            'label': fake.name(), 'limit': fake.numerify()
        }
        self.user = User.objects.create_user(
            'test_user1', 'test1@xyz.com', 'test_user1_password'
        )

    def tearDown(self):
        del self.user
        del self.client_obj

    def _make_post_request_for_user_profile(self, data, auth_token, key, secret):
        """
        Function to make a POST request to create User Profile instance.
        """
        response = self.client.post(
            reverse('accounts:user-profile'), data,
            HTTP_AUTHORIZATION='Token %s' % (auth_token),
            HTTP_AIRCTO_CLIENT_KEY=key,
            HTTP_AIRCTO_CLIENT_SECRET=secret
        )
        return response

    def test_user_profile_without_key_and_secret(self):
        response = self._make_post_request_for_user_profile(
            data=self.data, auth_token=self.user.auth_token.key,
            key='', secret=''
        )
        self.assertEqual(response.status_code, 500)

    def test_user_profile_with_invalid_token(self):
        response = self._make_post_request_for_user_profile(
            data=self.data, auth_token=self.user.auth_token.key + '.',
            key=self.client_obj.key, secret=self.client_obj.secret
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_with_invalid_key_and_secret(self):
        response = self._make_post_request_for_user_profile(
            data=self.data, auth_token=self.user.auth_token.key,
            key='dummy_key', secret='dummy_secret'
        )
        self.assertEqual(response.status_code, 500)

    def test_user_profile_with_valid_credentials(self):
        response = self._make_post_request_for_user_profile(
            data=self.data, auth_token=self.user.auth_token.key,
            key=self.client_obj.key, secret=self.client_obj.secret
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CreateUserProfileTests(APITestCase):
    """
    Test cases for creation of User Profile
    """
    def setUp(self):
        self.client_obj = ClientFactory()
        self.data = {'label': fake.name(), 'limit': fake.numerify()}
        self.user = User.objects.create_user(
            'test_user', 'test@xyz.com', 'test_user_password'
        )

    def tearDown(self):
        del self.user
        del self.client_obj

    def _make_post_request_for_user_profile(
        self, data, auth_token, key, secret):
        """
        Function to make a POST request to create User Profile instance.
        """
        response = self.client.post(
            reverse('accounts:user-profile'), data,
            HTTP_AUTHORIZATION='Token %s' % (auth_token),
            HTTP_AIRCTO_CLIENT_KEY=key,
            HTTP_AIRCTO_CLIENT_SECRET=secret
        )
        return response

    def test_create_user_profile(self):
        response = self._make_post_request_for_user_profile(
            data=self.data, auth_token=self.user.auth_token.key,
            key=self.client_obj.key, secret=self.client_obj.secret
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['token'])


class ClientKeySecretUniquenessTests(TestCase):
    """
    Test cases to check uniqueness of key and secret from existed ones
    """
    def test_client_key_uniqueness(self):
        client_key = generate_client_key()
        self.assertFalse(Client.objects.filter(key=client_key).exists())

    def test_client_secret_uniqueness(self):
        client_secret = generate_client_secret()
        self.assertFalse(Client.objects.filter(secret=client_secret).exists())

class UserViewTest(TestCase):

    def test_user_with_ideal_data(self):
        
