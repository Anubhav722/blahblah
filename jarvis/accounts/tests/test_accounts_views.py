from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from rest_framework import status

from jarvis.accounts.models import UserProfile, Client
from jarvis.accounts.views import UserView


class UserViewTest(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password')
		self.client = Client.objects.create(organization='Caped Crusaider')
		self.factory = APIRequestFactory()

	def test_user_without_providing_data(self):
		request = self.factory.post('/api/accounts', HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token),
			HTTP_AIRCTO_CLIENT_KEY=self.client.key, HTTP_AIRCTO_CLIENT_SECRET=self.client.secret)

		response = UserView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['limit'][0], 'This field is required.')
		self.assertEqual(response.data['label'][0], 'This field is required.')

	def test_userview_with_ideal_data(self):
		request = self.factory.post('/api/accounts', {'limit':'20', 'label':'dummy'},
			HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token),
			HTTP_AIRCTO_CLIENT_KEY=self.client.key, HTTP_AIRCTO_CLIENT_SECRET=self.client.secret)

		response = UserView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(len(response.data['token']), 40)
		self.assertEqual(response.data['label'], 'dummy')
