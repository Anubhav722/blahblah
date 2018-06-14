from django.test import TestCase
from django.conf import settings

from jarvis.resume.common import skill_match_percent
from jarvis.resume.models import Resume

class SkillMatchPercentTest(TestCase):

	def test_skill_match_percent(self):
		resume = Resume.objects.create(parse_status=0)
		skills = ['python']
		percent, matched_skills, matched_related_skills, related_skills_in_resume = skill_match_percent(resume, skills)

		self.assertEqual(percent, 0)

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()
		resume = Resume.objects.create(parse_status=0)
		resume.content = file
		resume.save()

		percent, matched_skills, matched_related_skills, related_skills_in_resume = skill_match_percent(resume, skills)

		self.assertEqual(percent, 100.0)
    	self.assertEqual(matched_skills, 'python')
