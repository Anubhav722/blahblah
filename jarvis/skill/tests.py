from django.test import TestCase

# Create your tests here.
from jarvis.skill.views import RelatedSkills

from rest_framework.test import APIRequestFactory
from rest_framework import status

class RelatedSkillsTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()

	def test_related_skills_for_provided_param(self):
		request = self.factory.get('/api/skill/related/?skills=python')
		response = RelatedSkills.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('message'), 'success')
		self.assertIn('data-science', response.data.get('related'))
		self.assertIn('data-analysis', response.data.get('related'))
		self.assertIn('natural-language-processing', response.data.get('related'))

	def test_related_skills_when_no_param_provided(self):
		request = self.factory.get('/api/skill/related/')
		response = RelatedSkills.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('related'), [])
