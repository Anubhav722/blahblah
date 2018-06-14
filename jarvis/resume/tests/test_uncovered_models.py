from django.test import TestCase
from django.conf import settings


from jarvis.resume.models import Url, Resume

class UrlTest(TestCase):

	def test_url(self):
		url = Url.objects.create(category='coding', url='http://url.com')

		self.assertEqual(url.category, 'coding')
		self.assertEqual(url.url, 'http://url.com')

		self.assertEqual(str(url), 'http://url.com')
