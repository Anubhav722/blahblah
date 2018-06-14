from django.test import TestCase
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.base import ContentFile

from jarvis.resume.models import Resume, Url, ResumeSkills, GitHub, StackOverflow, BitBucket, Blog, Website, MobileApp
# import resume
from jarvis.resume.helpers import (hireable,
	criteria_to_score,
	support_short_skill_names,
	get_related_technology_stack,
	parse_resume_internal,
	create_resume_instance,
	store_resume,
	get_basics,
	get_skill_matching_score,
	save_resume_skills,
	apply_github_score,
	apply_bitbucket_score)

from jarvis.resume.constants import SKILL_MAPPER, SHORT_SKILL_MAPPER, GOOD_HIRE, BAD_HIRE
# from jarvis.resume.utils.extractor import get_text
# from reusme.utils import parser_helper #import get_sim_hash_for_resume_content
from jarvis.resume.utils import *
from jarvis.resume.api import *

from uuid import uuid4, UUID
import os
import shutil
import datetime
from django.utils import timezone

class HireableFunctionTest(TestCase):
	def test_hireable_function_for_score_below_2_point_5(self):
		scores = [0, .5, 1.11111, 2.4444, 2.5]
		result = []
		for score in scores:
			result.append(hireable(score))

		self.assertEqual(result.count('bad-hire'), 4)
		self.assertEqual(result.count('good-hire'), 1)

	def test_hireable_function_for_score_above_2_point_5(self):
		scores = [2.5, 2.8, 3.0, 4.8, 4.99999, 5]
		result = []
		for score in scores:
			result.append(hireable(score))

		self.assertEqual(result.count('good-hire'), 6)

	def test_hireable_function_for_values_excluding_the_limit(self):
		scores = [-1, 5.4]
		result = []
		for score in scores:
			result.append(hireable(score))

		self.assertEqual(result.count('good-hire'), 0)
		self.assertEqual(result.count('bad-hire'), 0)

class TestCriteriaToScoreFunction(TestCase):

	def test_criteria_to_score_function(self):
		hires = ['good-hire', 'bad-hire', 'no-hire']
		result = []
		for hire in hires:
			result.append(criteria_to_score(hire))

		self.assertEqual(result.count(GOOD_HIRE), 1)
		self.assertEqual(result.count(BAD_HIRE), 2)

class SupportShortSkillNameTest(TestCase):

	def test_support_short_skill_names(self):
		skills = ['ror', 'psql', 'aws']
		result = []

		for skill in skills:
			result.append(support_short_skill_names(skill))

		self.assertIn(['ruby-on-rails', 'ruby', 'ror'], result)
		self.assertIn(['postgresql'], result)
		self.assertIn(['amazon-rds', 'amazonwebservices', 'devops', 'firehol', 'ansible', 'grafana', 'jenkins', 'kubernetes', 'amazon-web-services', 'aws', 'scalability', 'automation', 'docker'], result)

class GetTechnologyStackTest(TestCase):

	def test_get_related_technology_stack(self):
		skills = ['python', 'java', 'ruby']
		result = []

		for skill in skills:
			result.append(get_related_technology_stack(skill))

		self.assertIn(['flask', 'python', 'pyramid', 'tornado', 'django'], result)
		self.assertIn(['java', 'hibernate', 'apache-strut', 'java-me', 'java-ee', 'strut', 'java8', 'spring', 'java-se', 'sprint/play', 'play', 'apachestrut', 'j2se', 'j2me', 'j2ee'], result)
		self.assertIn(['ruby-on-rails', 'ruby', 'ror'], result)

class ParseResumeDataTest(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password')

	def test_parse_resume_internal(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		text = extractor.get_text(settings.TESTDATA_DIRS + 'view_tests/nda.pdf')
		file_name = 'nda.pdf'
		name, ext = os.path.splitext(file_name)

		uploaded_file_name = default_storage.save("%s" % uuid4() + ext, ContentFile(files.read()))
		path = default_storage.open(uploaded_file_name).name

		content_hash = parser_helper.get_sim_hash_for_resume_content(text)
		hash_value = content_hash.value

		resume = Resume.objects.create(user=self.user, parse_status=Resume.STATUS.processing)
		resume_id = resume.id

		resume_details = parse_resume_internal(path, text, resume_id, file_name, hash_value)

		self.assertEqual(resume_details.first_name, 'anubhav')
		self.assertEqual(resume_details.email, 'anubhavs286@gmail.com')
		self.assertEqual(resume_details.pk, resume_id)
		self.assertEqual(resume_details.phone_number, '+917697631870')
		self.assertEqual(resume_details.parse_status, 1)
		self.assertEqual(resume_details.urls.count(), 1)
		self.assertEqual(resume_details.urls.first().url, 'http://api.ai')

class CreateResumeInstanceTest(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password')

	def test_create_resume_instance(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		text = extractor.get_text(settings.TESTDATA_DIRS + 'view_tests/nda.pdf')
		file_name = 'nda.pdf'
		name, ext = os.path.splitext(file_name)

		uploaded_file_name = default_storage.save("%s" % uuid4() + ext, ContentFile(files.read()))
		path = default_storage.open(uploaded_file_name).name

		content_hash = parser_helper.get_sim_hash_for_resume_content(text)
		hash_value = content_hash.value

		serializer_data = create_resume_instance(path, text, file_name, hash_value, self.user)

		self.assertEqual(serializer_data.get('phone_number'), '+917697631870')
		self.assertEqual(serializer_data.get('first_name'), 'anubhav')
		self.assertEqual(serializer_data.get('email'), 'anubhavs286@gmail.com')
		self.assertEqual(serializer_data.get('urls')[0].get('url'), 'http://api.ai')

class StoreResumeTest(TestCase):

	def test_store_resume(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		file_name = 'nda.pdf'
		name, ext = os.path.splitext(file_name)
		path = store_resume(files, ext)

		self.assertNotEqual(path, None)
		self.assertEqual(path.split('/')[-1].split('.')[1], 'pdf')

class GetBasicsTest(TestCase):

	def test_get_basics(self):
		first_name, last_name, phone_number, email = get_basics(settings.TESTDATA_DIRS + 'view_tests/nda.pdf')

		self.assertEqual(first_name, 'anubhav')
		self.assertEqual(phone_number, '+917697631870')
		self.assertEqual(email, 'anubhavs286@gmail.com')
		self.assertEqual(last_name, 'singh')

class GetSkillMatchingScore(TestCase):

	def test_get_skill_matching_score(self):
		file_text = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		text = file_text.read()

		skills = 'python, python, django, javascript, git'
		(skill_match_score, skills_matched, skills_not_matched) = get_skill_matching_score(skills, text)

		self.assertEqual(skill_match_score, .75)
		self.assertEqual(skills_matched, 'python,git,django')
		self.assertEqual(skills_not_matched, 'javascript')

# class SaveResumeSkillsTest(TestCase):

# 	def setUp(self):
# 		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password')

# 	def test_save_resume_skills(self):
# 		import ipdb; ipdb.set_trace()
# 		resume = Resume.objects.create(user=self.user, parse_status=0)
# 		skills_matched = 'python,django,git'
# 		skills_not_matched = 'javascript'
# 		save_resume_skills(resume, skills_matched, skills_not_matched)

class GetTextViaOCRTest(TestCase):

	def test_get_text_via_ocr(self):
		text = extractor.get_text_via_ocr(settings.TESTDATA_DIRS + 'resume_extraction/00001.jpg')
		self.assertEqual(text.count('python'), 1)
		self.assertEqual(text.count('Anubhav'), 1)

class VerifyQualityTextTest(TestCase):

	def test_verify_quality_text(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		text = file_open.read()

		text_valid = extractor.verify_quality_text(text)

		self.assertEqual(text_valid, True)

class ParserTest(TestCase):

	def test_parser(self):

		candidate_info = parser.parser(settings.TESTDATA_DIRS + 'view_tests/nda.pdf')

		self.assertEqual(candidate_info['linkedin_user'], '')
		self.assertEqual(candidate_info['emails'][0], 'anubhavs286@gmail.com')
		self.assertEqual(candidate_info['names'][0], 'anubhav')

	def test_run_extractor(self):
		text = parser.run_extractor(settings.TESTDATA_DIRS + 'view_tests/nda.pdf')
		self.assertEqual(text.find('Anubhav Singh'), 32)

	def test_run_ocr(self):
		text = parser.run_ocr(settings.TESTDATA_DIRS + 'view_tests/nda.pdf')
		self.assertEqual(text.find('Anubhav Singh'), 0)
		self.assertEqual(text.find('Vikalp Khand'), 22)

	def test_get_alternative_name(self):
		linkedin_user = 'https://www.linkedin.com/in/anubhav-singh-16217911a/'
		github_user = 'https://github.com/Anubhav722'
		alternative_name = parser.get_alternative_name(linkedin_user, github_user)

		self.assertEqual(alternative_name, linkedin_user)

	def test_blacklist_scrubber(self):
		name = ['anubhav', 'contact']
		name_list = parser.blacklist_scrubber(name)

		self.assertEqual(name_list, ['anubhav'])

		name = []
		name_list = parser.blacklist_scrubber(name)
		self.assertEqual(name_list, [])

class ParserHelperFileTest(TestCase):

	def test_get_nums(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()
		phone_number = parser_helper.get_nums(file)

		file_open.close()
		self.assertEqual(phone_number, '+917697631870')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_11_digit_phone_number.txt')
		file = file_open.read()
		phone_number = parser_helper.get_nums(file)

		file_open.close()
		self.assertEqual(phone_number, '+917697631870,+917697631870')

	def test_get_course_discipline(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		response = parser_helper.get_course_discipline(file)

		self.assertEqual(response[0]['long_name'], 'bachelor of technology')
		self.assertEqual(response[0]['short_name'], 'b.tech')
		file_open.close()

	def test_get_email(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		response = parser_helper.get_email(file)

		self.assertEqual(response[0], 'anubhavs286@gmail.com')
		file_open.close()

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_email.txt')
		file = file_open.read()

		response = parser_helper.get_email(file)

		file_open.close(response, None)

	def test_get_linkedin(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_linked_in.txt')
		file = file_open.read()

		response = parser_helper.get_linkedin(file)
		file_open.close()
		self.assertEqual(response[0], 'https://www.linkedin.com/in/anubhav-singh-16217911a/')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_extraction.txt')
		file = file_open.read()
		response = parser_helper.get_linkedin(file)
		self.assertEqual(response, None)

		file_open.close()

	def test_get_github(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_github.txt')
		file = file_open.read()

		response = parser_helper.get_github(file)
		file_open.close()
		self.assertEqual(response[0], 'https://github.com/Anubhav722')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		response = parser_helper.get_github(file)
		file_open.close()

		self.assertEqual(response, None)

	def test_get_id_from_linkedin_url(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_linked_in.txt')
		file = file_open.read()

		response = parser_helper.get_id_from_linkedin_url(file)
		file_open.close()

		self.assertEqual(response, 'anubhav-singh-16217911a')


	def test_get_username_from_github_url(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_github.txt')
		file = file_open.read()
		response = parser_helper.get_username_from_github_url(file)
		file_open.close()

		self.assertEqual(response, 'Anubhav722')

	def test_get_name_data_from_email(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()
		response = parser_helper.get_name_data_from_email(file)
		file_open.close()

		self.assertEqual(response[0], 'anubhavs')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_email.txt')
		file = file_open.read()
		response = parser_helper.get_name_data_from_email(file)
		file_open.close()

		self.assertEqual(response, None)

	def test_get_name_candidates_from_email(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		response = parser_helper.get_name_candidates_from_email(file)
		file_open.close()

		self.assertIn('anubhav', response)

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_email.txt')
		file = file_open.read()

		response = parser_helper.get_name_candidates_from_email(file)
		self.assertEqual(response, None)

	def test_get_name(self):

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()
		response = parser_helper.get_name(file)
		file_open.close()

		self.assertEqual(response[0], 'anubhav')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_email.txt')
		file = file_open.read()
		response = parser_helper.get_name(file)
		file_open.close()
		self.assertEqual(response, None)

	def test_compare_email_line(self):

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		original_text = file
		first_line = original_text.split('\n')[0]

		response = parser_helper.compare_email_line(original_text.lower(), first_line)

		self.assertEqual(response, True)
		file_open.close()
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_without_email.txt')
		file = file_open.read()

		original_text = file
		first_line = original_text.split('\n')[0]

		response = parser_helper.compare_email_line(original_text.lower(), first_line)

		self.assertEqual(response, None)

	def test_get_repo_details(self):
		user_name = 'Anubhav722'
		repo = 'Facebook-Messenger-Chat-Bot'
		response = parser_helper.get_repo_details(user_name, repo)

		self.assertEqual(reponse[url], 'https://github.com/Anubhav722/Facebook-Messenger-Chat-Bot')


	def test_get_github_username(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_github.txt')
		file = file_open.read()

		match = parser_helper.get_github_username(file)

		file_open.close()

		self.assertEqual(match, 'Anubhav722')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		match = parser_helper.get_github_username(file)
		file_open.close()

		self.assertEqual(match, None)

	def test_get_stackoverflow_userid(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_stackoverflow.txt')
		file = file_open.read()

		file_open.close()
		user_id = parser_helper.get_stackoverflow_userid(file)
		self.assertEqual(user_id, '6657230')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		file_open.close()
		user_id = parser_helper.get_stackoverflow_userid(file)
		self.assertEqual(user_id, None)


	def test_get_stackoverflow_username(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_stackoverflow.txt')
		file = file_open.read()

		file_open.close()
		username = parser_helper.get_stackoverflow_username(file)

		self.assertEqual(username, 'anubhav-singh')

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()

		username = parser_helper.get_stackoverflow_username(file)

		file_open.close()
		self.assertEqual(username, None)

	def test_get_urls(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = file_open.read()
		file_open.close()

		urls = parser_helper.get_urls(file)

		self.assertEqual('api.ai', urls[0])

		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/resume_with_stackoverflow.txt')
		file = file_open.read()
		file_open.close()

		urls = parser_helper.get_urls(file)

		self.assertEqual(['https://stackoverflow.com/users/6657230/anubhav-singh', 'api.ai'], urls)

	def test_url_summary(self):
		urls = ['https://stackoverflow.com/users/6657230/anubhav-singh', 'https://api.ai']
		results = []
		for url in urls:
			sentences = parser_helper.url_summary(url)
			results.append(sentences)

			self.assertEqual(type(sentences), list)

	def test_url_categories(self):
		urls = ['https://stackoverflow.com/users/6657230/anubhav-singh', 'https://api.ai', 'https://github.com/Anubhav722']
		results = []
		categories = parser_helper.url_categories(urls)
		self.assertEqual(categories['contributions'][0], 'https://github.com/Anubhav722')
		self.assertEqual(categories['others'][0], 'https://api.ai')
		self.assertEqual(categories['forums'][0], 'https://stackoverflow.com/users/6657230/anubhav-singh')


	def test_get_url_response(self):
		categories = {'coding': [], 'contributions': ['https://github.com/Anubhav722'], 'others': ['https://api.ai'], 'apps': [], 'blog': [], 'social': [], 'forums': ['https://stackoverflow.com/users/6657230/anubhav-singh']}
		url_response = parser_helper.get_url_response(categories)
		self.assertEqual(url_response, [{'type': 'others', 'name': 'https://api.ai'}, {'type': 'forums', 'name': 'https://stackoverflow.com/users/6657230/anubhav-singh'}, {'type': 'contributions', 'name': 'https://github.com/anubhav722'}])

	def test_get_bitbucket_url(self):
		contribution_urls = ['https://bitbucket.org/Anubhav_722/']
		url = parser_helper.get_bitbucket_url(contribution_urls)
		self.assertEqual(url, 'https://bitbucket.org/Anubhav_722/')

	def test_get_bitbucket_username(self):
		bitbucket_url = 'https://bitbucket.org/Anubhav_722/'
		bitbucket_username = parser_helper.get_bitbucket_url(bitbucket_url)
		self.assertEqual(bitbucket_username, 'Anubhav_722')

	def test_get_standard_indian_format_number(self):
		text = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		file = text.read()
		numbers_list = parser_helper.get_standard_indian_format_number(file)
		text.close()
		self.assertEqual(numbers_list[0], '+917697631870')

	def test_get_sim_hash_for_resume_content(self):
		file_open = open(settings.TESTDATA_DIRS + 'resume_extraction/ideal_resume_data.txt')
		content = file_open.read()
		hash_object = parser_helper.get_sim_hash_for_resume_content(content)
		self.assertEqual(hash_object.value.bit_length(), 128)

class GetGithubScores(TestCase):

	def test_get_github_scores(self):
		resume_instance = Resume.objects.create(parse_status=0)
		instance = GitHub.objects.create(resume=resume_instance, user_id=21,
			user_name='Anubhav722', profile_name='Anubhav Singh',
			email='anubhavs286@gmail.com', profile_url='https://github.com/Anubhav722',
			profile_image_url='https://avatars0.githubusercontent.com/u/20791676?v=3&u=632370288e6e7a077811ddbfd4a1a654fb6f9130&s=400',
			gists_url='https://gist.github.com/', location='Bangalore', contribution_score=.4,
			activity_score=.3, reputation_score=.2, company='Launchyard', followers=6, following=15,
			hireable=True, public_repos=12, blog_url='https://tumblr.com', owned_private_repos=0,
			public_gists=4, private_gists=3, total_private_repos=137, account_created_at=datetime.datetime.now().date(),
			account_modified_at=timezone.now(), repo_updated_at=timezone.now())

		github_contribution_score, github_activity_score, github_reputation_score = helpers.get_github_scores(GitHub.objects.all())

		self.assertEqual(github_contribution_score, .4)
		self.assertEqual(github_activity_score, .3)
		self.assertEqual(github_reputation_score, .2)


class GetStackOverFlowScore(TestCase):

	def test_stackoverflow_score(self):
		resume_instance = Resume.objects.create(parse_status=0)
		instance = StackOverflow.objects.create(user_id=123, resume=resume_instance,
			profile_name='Anubhav', location='Bangalore', website_url='https://blog.com',
			profile_url='https://profile.com', profile_image_url='https://image.com',
			reputation=2, gold_badges_count=1, silver_badges_count=2, bronze_badges_count=3,
			account_creation_date=timezone.now(), last_access_date=timezone.now(),
			is_moderator=False, total_no_questions=5, total_no_answers=3, reputation_change_month=1,
			reputation_change_quarter=1, reputation_change_year=1, reputation_score=.35,
			contribution_score=.8, activity_score=.75)

		contribution_score, reputation_score, activity_score = helpers.get_stackoverflow_scores(StackOverflow.objects.all())

		self.assertEqual(contribution_score, .8)
		self.assertEqual(reputation_score, .35)
		self.assertEqual(activity_score, .75)

class GetBitBucketScore(TestCase):

	def test_get_bitbucket_scores(self):
		resume = Resume.objects.create(parse_status=0)
		instance = BitBucket.objects.create(resume=resume, user_name='ANUBHAV_722',
			display_name='Anubhav722', account_created_at=timezone.now(),
			total_no_public_repos=12, following=0, followers=3, blog_url='https://blog.com',
			profile_url='https://profile.com', repositories_url='https://repo.com',
			snippet_url='https://snippet.com', location='Bangalore', reputation_score=2,
			contribution_score=1, activity_score=2)

		contribution_score, reputation_score, activity_score = helpers.get_bitbucket_scores(BitBucket.objects.all())

		self.assertEqual(contribution_score, 1)
		self.assertEqual(reputation_score, 2)
		self.assertEqual(activity_score, 2)

class GetBlogScore(TestCase):

	def test_get_blog_scores(self):
		resume = Resume.objects.create(parse_status=0)
		instance = Blog.objects.create(resume=resume, reputation_score=1,
			contribution_score=2, activity_score=3)

		contribution_score, reputation_score, activity_score = helpers.get_blog_scores(Blog.objects.all())

		self.assertEqual(contribution_score, 2)
		self.assertEqual(reputation_score, 1)
		self.assertEqual(activity_score, 3)

class WebsiteScore(TestCase):

	def test_get_website_scores(self):
		resume = Resume.objects.create(parse_status=0)
		instance = Website.objects.create(resume=resume, reputation_score=1,
			contribution_score=2, activity_score=3)

		contribution_score, reputation_score, activity_score = helpers.get_website_scores(Website.objects.all())

		self.assertEqual(contribution_score, 2)
		self.assertEqual(activity_score, 1)
		self.assertEqual(reputation_score, 3)

class MobileAppScore(TestCase):

	def test_get_app_scores(self):
		resume = Resume.objects.create(parse_status=0)
		instance = MobileApp.objects.create(resume=resume, app_type='blah',
			app_url='https://app.com', rating_ios=3, customer_rating_for_all_version_ios=2.8,
			customer_rating_for_current_version_ios=2.9, total_customer_rating=3.1,
			last_updated_date=datetime.datetime.now().date(), ratings_android=4.4,
			installs_android=1580, reputation_score=1, contribution_score=2, activity_score=3)

		contribution_score, activity_score, reputation_score = helpers.get_app_scores(MobileApp.objects.all())

		self.assertEqual(contribution_score, 2)
		self.assertEqual(activity_score, 3)
		self.assertEqual(reputation_score,1)

class GetYearsAndMonthsTest(TestCase):

	def test_get_years_and_months(self):
		# import ipdb; ipdb.set_trace()
		resume = Resume.objects.create(parse_status=0)
		years = 0
		months = 1
		days = 12
		account_created, days = helpers.get_years_and_months(str(years), str(months), str(days))
		self.assertEqual(account_created, '1 mo')
		self.assertEqual(days, '12 days')

		account_created, days = helpers.get_years_and_months(str(0), str(0), str(1))
		self.assertEqual(account_created, 'Today')
		self.assertEqual(days, '1 days')

		account_created, days = helpers.get_years_and_months(str(0), str(2), str(0))
		self.assertEqual(account_created, '2 mos')
		self.assertEqual(days, '0 days')

		account_created, days = helpers.get_years_and_months(str(1), str(0), str(1))
		self.assertEqual(account_created, '1 yr')
		self.assertEqual(days, '1 days')

		account_created, days = helpers.get_years_and_months(str(1), str(1), str(0))
		self.assertEqual(account_created, '1 yr 1 mo')
		self.assertEqual(days, '0 days')

		account_created, days = helpers.get_years_and_months(str(2), str(0), str(0))
		self.assertEqual(account_created, '2 yrs')
		self.assertEqual(days, '0 days')

		account_created, days = helpers.get_years_and_months(str(2), str(1), str(0))
		self.assertEqual(account_created, '2 yrs 1 mo')
		self.assertEqual(days, '0 days')

		account_created, days = helpers.get_years_and_months(str(2), str(3), str(0))
		self.assertEqual(account_created, '2 yrs 3 mos')
		self.assertEqual(days, '0 days')

class GetStackOverflowDetails(TestCase):

	def test_get_stackoverflow_details(self):
		resume_instance = Resume.objects.create(parse_status=0)
		instance = StackOverflow.objects.create(user_id=123, resume=resume_instance,
			profile_name='Anubhav', location='Bangalore', website_url='https://blog.com',
			profile_url='https://profile.com', profile_image_url='https://image.com',
			reputation=2, gold_badges_count=1, silver_badges_count=2, bronze_badges_count=3,
			account_creation_date=timezone.now(), last_access_date=timezone.now(),
			is_moderator=False, total_no_questions=5, total_no_answers=3, reputation_change_month=1,
			reputation_change_quarter=1, reputation_change_year=1, reputation_score=.35,
			contribution_score=.8, activity_score=.75)

		details = helpers.get_stackoverflow_details(instance)

		self.assertEqual(len(details), 8)

class GetGitHubDetails(TestCase):

	def test_get_github_details(self):
		resume_instance = Resume.objects.create(parse_status=0)
		instance = GitHub.objects.create(resume=resume_instance, user_id=21,
			user_name='Anubhav722', profile_name='Anubhav Singh',
			email='anubhavs286@gmail.com', profile_url='https://github.com/Anubhav722',
			profile_image_url='https://avatars0.githubusercontent.com/u/20791676?v=3&u=632370288e6e7a077811ddbfd4a1a654fb6f9130&s=400',
			gists_url='https://gist.github.com/', location='Bangalore', contribution_score=.4,
			activity_score=.3, reputation_score=.2, company='Launchyard', followers=6, following=15,
			hireable=True, public_repos=12, blog_url='https://tumblr.com', owned_private_repos=0,
			public_gists=4, private_gists=3, total_private_repos=137, account_created_at=datetime.datetime.now().date(),
			account_modified_at=timezone.now(), repo_updated_at=timezone.now())

		details = helpers.get_github_details(instance)

		self.assertEqual(len(details), 6)

class GetBitBucketDetails(TestCase):

	def test_get_bitbucket_details(self):
		resume = Resume.objects.create(parse_status=0)
		instance = BitBucket.objects.create(resume=resume, user_name='ANUBHAV_722',
			display_name='Anubhav722', account_created_at=timezone.now(),
			total_no_public_repos=12, following=0, followers=3, blog_url='https://blog.com',
			profile_url='https://profile.com', repositories_url='https://repo.com',
			snippet_url='https://snippet.com', location='Bangalore', reputation_score=2,
			contribution_score=1, activity_score=2)

		details = helpers.get_bitbucket_details(instance)

		self.assertEqual(len(details), 4)

class GetBlogDetails(TestCase):

	def test_get_blog_details(self):
		resume = Resume.objects.create(parse_status=0)
		instance = Blog.objects.create(resume=resume, reputation_score=1,
			contribution_score=2, activity_score=3, url='tumblr.com/blog/i-psychoassassin')

		details = helpers.get_blog_details(instance)

		self.assertEqual(len(details), 2)

class GetWebsiteDetails(TestCase):

	def test_get_website_details(self):
		resume = Resume.objects.create(parse_status=0)
		instance = Website.objects.create(resume=resume, reputation_score=1,
			contribution_score=2, activity_score=3, url='tumblr.com/blog/i-psychoassassin')

		details = helpers.get_website_details(instance, 'anubhavs286@gmail.com')

		self.assertEqual(len(details), 2)

class GetTotalScore(TestCase):

	def test_get_total_score(self):
		resume = Resume.objects.create(parse_status=0)
		instance = MobileApp.objects.create(resume=resume, app_type='blah',
			app_url='https://app.com', rating_ios=3, customer_rating_for_all_version_ios=2.8,
			customer_rating_for_current_version_ios=2.9, total_customer_rating=3.1,
			last_updated_date=datetime.datetime.now().date(), ratings_android=4.4,
			installs_android=1580, reputation_score=1, contribution_score=2, activity_score=3)

		score = helpers.get_total_score(MobileApp.objects.all())

		self.assertEqual(details, .6)

class GetIOSData(TestCase):

	def test_get_ios_data(self):
		resume = Resume.objects.create(parse_status=0)
		instance = MobileApp.objects.create(resume=resume, app_type='blah',
			app_url='https://app.com', rating_ios=3, customer_rating_for_all_version_ios=2.8,
			customer_rating_for_current_version_ios=2.9, total_customer_rating=3.1,
			last_updated_date=datetime.datetime.now().date(), ratings_android=4.4,
			installs_android=1580, reputation_score=1, contribution_score=2, activity_score=3)

		data = helpers.get_ios_data(MobileApp.objects.all())

		self.assertEqual(len(data), 5)

	def test_get_ios_urls(self):
		resume = Resume.objects.create(parse_status=0)
		instance = MobileApp.objects.create(resume=resume, app_type='blah',
			app_url='https://app.com', rating_ios=3, customer_rating_for_all_version_ios=2.8,
			customer_rating_for_current_version_ios=2.9, total_customer_rating=3.1,
			last_updated_date=datetime.datetime.now().date(), ratings_android=4.4,
			installs_android=1580, reputation_score=1, contribution_score=2, activity_score=3)

		url_list = helpers.get_ios_urls(MobileApp.objects.all())

		self.assertEqual(url_list[0], 'https://app.com')

class BitBucketUserDetails(TestCase):

	def test_bit_bucket_user_details(self):
		username = 'Anubhav_722'
		user_details = extractor.bit_bucket_user_details(username)

		self.assertEqual(user_details['user_name'], 'Anubhav_722')
		self.assertEqual(user_details['profile_url'], 'https://bitbucket.org/Anubhav_722/')


class ApplyGitHubScore(TestCase):

	def test_apply_github_score(self):
		username = 'Anubhav722'
		resume = Resume.objects.create(parse_status=0)

		activity_score, reputation_score, contribution_score = apply_github_score(username, resume)

		self.assertTrue(activity_score is not None)
		self.assertTrue(contribution_score is not None)
		self.assertTrue(reputation_score is not None)

class ApplyBitBucketScore(TestCase):

	def test_apply_bitbucket_score(self):
		username = 'Anubhav_722'
		resume = Resume.objects.create(parse_status=0)

		activity_score, reputation_score, contribution_score = apply_bitbucket_score(username, resume)

		self.assertTrue(activity_score is not None)
		self.assertTrue(reputation_score is not None)
		self.assertTrue(contribution_score is not None)

class GetAndroidData(TestCase):

	def test_get_android_data(self):
		resume = Resume.objects.create(parse_status=0)
		instance = MobileApp.objects.create(resume=resume, app_type='blah',
			app_url='https://app.com', rating_ios=3, customer_rating_for_all_version_ios=2.8,
			customer_rating_for_current_version_ios=2.9, total_customer_rating=3.1,
			last_updated_date=datetime.datetime.now().date(), ratings_android=4.4,
			installs_android=1580, reputation_score=1, contribution_score=2, activity_score=3)

		data = helpers.get_android_data(MobileApp.objects.all())

		self.assertEqual(len(data), 3)
		self.assertEqual(data[0]['name'], 'Total Rating')
		self.assertEqual(data[1]['name'], 'App Installs')
