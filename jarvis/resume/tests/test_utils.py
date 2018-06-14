from django.test import TestCase
from jarvis.resume.utils.extractor import get_text
from jarvis.resume.utils.parser_helper import get_urls, get_url_response, url_categories, get_github_username, get_stackoverflow_userid, get_stackoverflow_username, get_name, get_id_from_linkedin_url, get_email
from unidecode import unidecode


path_to_test_data = 'resume/tests/test_data/1.pdf'

urls = ['https://github.com/imnithin', 'http://imnithin.github.io', 'https://gist.github.com/imnithin',
                'http://stackoverflow.com/users/2231236/nithin', 'https://www.linkedin.com/in/imnithink']

categories = {'blog': ['http://imnithin.github.io'], 'coding': [],
                      'contributions': ['https://github.com/imnithin', 'https://gist.github.com/imnithin'],
                      'forums': ['http://stackoverflow.com/users/2231236/nithin'],  'others': [],
                      'social': ['https://www.linkedin.com/in/imnithink']}

url_response = [{'name': 'https://github.com/imnithin', 'type': 'contributions'},
                {'name': 'https://gist.github.com/imnithin', 'type': 'contributions'},
                {'name': 'https://www.linkedin.com/in/imnithink', 'type': 'social'},
                {'name': 'http://imnithin.github.io', 'type': 'blog'},
                {'name': 'http://stackoverflow.com/users/2231236/nithin', 'type': 'forums'}]


class ParserHelperUtilsTest(TestCase):
    """Unit tests for Parser Helper Functions"""

    def setUp(self):
        self.text = get_text(path_to_test_data)

    def test_get_name(self):
        """Test User Name Obtained from jarvis.resume"""
        name = 'nithin'
        self.assertEqual(get_name(self.text)[0], name)

    def test_github_username(self):
        """Test GitHub Username"""
        github_user_name = 'imnithin'
        self.assertEqual(get_github_username(self.text), github_user_name)

    def test_stackoverflow_user_id(self):
        """Test StackOverflow user id"""
        stackoverflow_user_id = '2231236'
        self.assertEqual(get_stackoverflow_userid(self.text), stackoverflow_user_id)

    def test_stackoverflow_user_name(self):
        """Test StackOverflow User Name"""
        stackoverflow_user_name = 'nithin'
        self.assertEqual(get_stackoverflow_username(self.text), stackoverflow_user_name)

    def test_get_urls(self):
        self.assertEqual(get_urls(self.text), urls)

    def test_url_categories(self):
        values = list(categories.values()).sort()
        self.assertEqual(list(url_categories(urls).values()).sort(), values)

    def test_get_url_response(self):
        sorted_url_response = url_response.sort()
        self.assertEqual(get_url_response(categories).sort(), sorted_url_response)

    def test_get_id_from_linkedin_url(self):
        linkedin_id = 'imnithink'
        self.assertEqual(unidecode(get_id_from_linkedin_url(self.text)).strip(), linkedin_id)

    def test_get_email(self):
        email = 'nithinkool14@gmail.com'
        self.assertEqual(get_email(self.text)[0], email)

