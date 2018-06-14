from django.test import TestCase
from django.conf import settings

from jarvis.resume.helpers import get_basics
from jarvis.resume.utils.parser_helper import get_urls, url_categories

from jarvis.resume.utils.machine_learning.features import ExtractFeatures
from jarvis.resume.utils.machine_learning.helper import FeatureExtraction


class ResumeExtraction(TestCase):
	"""
	Test for resume extraction:
	Asserts for first_name, last_name,
	Year's experience
	"""
	fixtures = ['fixtures/all_locations.json', 'fixtures/all_companies.json', 'fixtures/all_institutions.json']

	def setUp(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt', 'r')
		self.ideal_resume_data = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_name.txt', 'r')
		self.resume_without_name = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_experience.txt', 'r')
		self.resume_with_experience = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_email.txt', 'r')
		self.resume_without_email = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_known_institute.txt', 'r')
		self.resume_with_known_institute = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_known_company.txt', 'r')
		self.resume_with_known_company = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_3_locations.txt', 'r')
		self.resume_with_3_locations = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_11_digit_phone_number.txt', 'r')
		self.resume_with_11_digit_phone_number = file_open.read()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_wrong_email.txt', 'r')
		self.resume_with_wrong_email = file_open.read()

		self.extract_features = ExtractFeatures()


	def test_resume_urls_and_their_categories(self):
		ideal_resume_urls = get_urls(self.ideal_resume_data)
		resume_without_name_urls = get_urls(self.resume_without_name)

		self.assertEqual(len(ideal_resume_urls), 1)
		self.assertEqual(ideal_resume_urls[0], 'api.ai')

		self.assertEqual(len(resume_without_name_urls), 1)
		self.assertEqual(resume_without_name_urls[0], 'api.ai')

		category_urls = url_categories(ideal_resume_urls)
		category_of_without_name_urls = url_categories(resume_without_name_urls)

		self.assertEqual(category_of_without_name_urls['others'][0], 'http://api.ai')
		self.assertEqual(category_urls['others'][0], 'http://api.ai')


	def test_resume_basic_user_info_extraction(self):
		first_name, last_name, phone_number, email = get_basics(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		first_name_2, last_name_2, phone_number_2, email_2 = get_basics(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_name.txt')
		first_name_3, last_name_3, phone_number_3, email_3 = get_basics(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_email.txt')
		first_name_4, last_name_4, phone_number_4, email_4 = get_basics(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_11_digit_phone_number.txt')
		first_name_5, last_name_5, phone_number_5, email_5 = get_basics(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_wrong_email.txt')

		self.assertNotEqual(email_5, 'anubhavs286@gmaila.coma')
		self.assertNotEqual(email_5, 'anubhavs286@gmaila.com')
		self.assertEqual(email_5, '')

		self.assertIn(first_name_4, 'anubhav')
		self.assertIn(last_name_4, 'singh')
		self.assertNotEqual(phone_number_4, '+916976318701')
		self.assertIn(email_4, 'anubhavs286@gmail.com')

		self.assertEqual(first_name_3, 'anubhav')
		self.assertEqual(last_name_3, 'singh')
		self.assertEqual(phone_number_3, '+917697631870')
		self.assertEqual(email_3, '')

		self.assertEqual(first_name, 'anubhav')
		self.assertEqual(last_name, 'singh')
		self.assertEqual(phone_number, '+917697631870')
		self.assertEqual(email, 'anubhavs286@gmail.com')

		self.assertEqual(first_name_2, '')
		self.assertEqual(last_name_2, '')
		self.assertEqual(phone_number_2, '+917697631870')
		self.assertEqual(email_2, 'anubhavs286@gmail.com')


	def test_years_of_experience(self):
		features = FeatureExtraction()

		work_experience = features.get_work_experience(self.ideal_resume_data)

		work_experience_added = features.get_work_experience(self.resume_with_experience)

		self.assertEqual(work_experience_added, '1')
		self.assertEqual(work_experience, '.33')


	def test_users_previous_companies(self):
		companies = self.extract_features.get_company_names(self.ideal_resume_data)

		known_companies = self.extract_features.get_company_names(self.resume_with_known_company)

		self.assertEqual(['facebook', 'google', 'amazon', 'quora'], known_companies)

		self.assertIn('platform media and company', companies)
		self.assertIn('paytm', companies)


	def test_users_location(self):

		locations = self.extract_features.get_location(self.ideal_resume_data)

		three_locations = self.extract_features.get_location(self.resume_with_3_locations)

		self.assertEqual(['lucknow', 'kanpur', 'bangalore'], three_locations)

		self.assertIn('lucknow', locations)


	def test_users_institutions(self):

		institutions = self.extract_features.get_institution_names(self.ideal_resume_data)

		known_institute = self.extract_features.get_institution_names(self.resume_with_known_institute)

		self.assertIn('indian institute of technology, kanpur', known_institute)

		self.assertIn('jaypee university of engineering and technology', institutions)

