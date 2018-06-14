from django.test import TestCase
from django.contrib.auth.models import User#, UserProfile
from django.db.models.signals import pre_save, post_save
from django.dispatch import Signal

from jarvis.accounts.signals.handlers import create_client_key_and_secret
# from jarvis.accounts.models import Client, UserProfile
import jarvis.accounts
# from unittest.mock import patch
import mock

# @patch('accounts/signals/handlers.py')
# class CreateClientKeyAndSecret(TestCase):

# 	def test_create_client_key_and_secret(self):
# 		# with mock.patch('accounts.signals.handlers.create_client_key_and_secret', autospec=True) as mocked_handler:
# 		# 	pre_save.connect(mocked_handler, sender=User, dispatch_uid='client-key-and-client-secret-creation-signal')
# 		pre_save.connect(accounts.signals.handlers.create_client_key_and_secret)
# 		import ipdb; ipdb.set_trace()
# 		client = accounts.models.Client.objects.create(organization='chess')

class CreateClientKeyAndSecret(TestCase):

	def test_create_client_key_and_secret(self):
		client = accounts.models.Client.objects.create(organization='chess')
		create_client_key_and_secret(sender=accounts.models.Client, instance=client, created=True)

		self.assertEqual(len(client.key), 40)
		self.assertEqual(len(client.secret), 64)


	def test_create_access_token_for_user(self):
		user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password')
		self.assertEqual(len(user.auth_token.key), 40)

	def test_create_user_profile(self):
		user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password')

		self.assertEqual(user, accounts.models.UserProfile.objects.first().user)
