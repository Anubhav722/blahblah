from django.test import TestCase
from django.conf import settings

from jarvis.resume.utils.machine_learning.helper import (get_tokens,
	remove_stop_words,
	remove_punctuation,
	FeatureExtraction)

class GetTokensTest(TestCase):

	def setUp(self):
		self.file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		self.file = self.file_open.read()
		self.file_open.close()

	def test_get_tokens(self):

		tokens = get_tokens(self.file)
		self.assertEqual(tokens.count('python'), 2)

	def test_remove_stop_words(self):

		tokens = get_tokens(self.file)
		filtered_text = remove_stop_words(tokens)

		self.assertEqual(filtered_text.count('python'), 2)

	def test_remove_punctuation(self):
		tokens = remove_punctuation(self.file)

		self.assertEqual(token.count('python'), 2)

	def test_summarizer(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_experience.txt')
		text = file_open.read()
		features = FeatureExtraction()
		freq = features.summarize(text, 3)

		self.assertEqual(len(freq), 3)

	def test_get_year_of_experience(self):
		experience_info = ['Experience: 1yr']
		features = FeatureExtraction()
		yoe = features.get_year_of_experience(experience_info)

		self.assertEqual(yoe, 1)

		experience_info = ['Experience: 1yr, 2months']
		yoe = features.get_year_of_experience(experience_info)

		self.assertEqual(yoe, 1)
