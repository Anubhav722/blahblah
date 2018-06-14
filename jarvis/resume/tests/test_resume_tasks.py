from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from jarvis.resume import tasks

from jarvis.resume.models import Resume
from jarvis.resume.utils.parser_helper import get_sim_hash_for_resume_content

import shutil

class ParseResumeTest(TestCase):

	def test_parse_resume(self):
		path = settings.TESTDATA_DIRS + 'view_tests/nda.pdf'
		file = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		text = file.read()
		file.close()
		resume = Resume.objects.create(parse_status=0, content=text)
		resume_id = resume.id
		skills = 'python, django'
		file_name = 'nda.pdf'

		content_hash = get_sim_hash_for_resume_content(text)
		hash_value = content_hash.value

		result = tasks.parse_resume(path, text, resume_id, skills, file_name, hash_value)

		self.assertEqual(result, 'Resume Processed')
