from .factories import UrlFactory, ResumeFactory
from django.test import TestCase
from jarvis.resume.api.serializers import UrlSerializer, ResumeSerializer


class UrlSerializerTest(TestCase):
    """
    Unit test for Url Serializer and De Serializer
    """
    def setUp(self):
        self.solution = UrlFactory()

    def test_representation_data(self):
        expected_keys = ['url', 'category']
        serializer = UrlSerializer(self.solution)
        keys = list(serializer.data.keys())
        self.assertEqual(sorted(keys), sorted(expected_keys))

    def test_data(self):
        serializer = UrlSerializer(self.solution)
        self.assertEqual(serializer.data['url'], self.solution.url)
        self.assertEqual(serializer.data['category'], self.solution.category)


class ResumeSerializerTest(TestCase):
    """
    Unit test for UserResume Serializer and De Serializer
    """
    def setUp(self):
        self.solution = ResumeFactory()

    def test_representation_data(self):
        expected_keys = ['first_name', 'last_name', 'email', 'experience', 'file_name', 'phone_number', 'score',
                         'parse_status', 'id', 'urls', 'resume_location', 'created_date']
        serializer = ResumeSerializer(self.solution)
        keys = list(serializer.data.keys())
        self.assertEqual(sorted(keys), sorted(expected_keys))

    def test_data(self):
        serializer = ResumeSerializer(self.solution)
        self.assertEqual(serializer.data['first_name'], self.solution.first_name)
        self.assertEqual(serializer.data['last_name'], self.solution.last_name)
        self.assertEqual(serializer.data['email'], self.solution.email)
        self.assertEqual(serializer.data['file_name'], self.solution.file_name)
        self.assertEqual(serializer.data['phone_number'], self.solution.phone_number)
        self.assertEqual(serializer.data['parse_status'], self.solution.parse_status)
        self.assertEqual(serializer.data['id'], self.solution.id)
        self.assertEqual(serializer.data['experience'], self.solution.experience)
        self.assertEqual(serializer.data['resume_location'], self.solution.resume_location)
