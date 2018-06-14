from django.test import TestCase
from django.contrib.auth import get_user_model


from .factories import UserProfileFactory
from jarvis.accounts.models import UserProfile, Client

from faker import Faker
faker = Faker()

User = get_user_model()


class UserProfileTests(TestCase):
    """
    Test cases for User Profile
    """
    def setUp(self):
    	self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')
        self.profile = UserProfileFactory()

    def tearDown(self):
        del self.profile

    def test_auth_token_creation(self):
        self.assertTrue(self.profile.user.auth_token)

    def test_userprofile_limit_field(self):
    	user_profile = UserProfile(limit=80, user=self.user)
        user_profile.save()
    	self.assertEqual(user_profile.limit, 80)

    def test_userprofile_and_client_model_relation(self):
    	clients = Client.objects.create(key='You will..!!', secret="robin is actually batman's intern", organization='launchyard')
    	user_profile = UserProfile(client=clients, user=self.user, label='Batman')
    	self.assertEqual(user_profile.client, clients)

class ClientTests(TestCase):
	"""
	Test Cases for Client
	"""

    def test_client_model_string_representation(self):
        client = Client(key='Do you bleed??', secret='You will..!', organization='Batman')
        client.save()
        self.assertEqual(str(client), 'Batman')

    def test_client_model_autogenerate_client_key_and_secret(self):
		client = Client.objects.create(organization='Batman')
        self.assertTrue(client.key is not None)
        self.assertTrue(client.secret is not None)

