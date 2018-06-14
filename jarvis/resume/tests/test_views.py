from django.test import TestCase
from unittest import TestCase as Tc
from jarvis.resume.views import Resume
from django.test import RequestFactory


class HomePageTest(TestCase):

    def test_post_url(self):
        response = self.client.post('api/resume/')
        self.assertEqual(response.status_code, 404)

    def url_category(self):
        response = self.client.post('api/resume/')
        self.assertEqual(response.status_code, 200)


class ResumeViewTestCase(Tc):
    def test_get(self):
        request = RequestFactory().get('api/resume/')
        view = Resume.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 401)


