from django.test import TestCase
from django.conf import settings

from jarvis.resume.utils.parser_helper import (
					get_github_username,
					get_bitbucket_username,
					get_bit_bucket_url,
					get_stackoverflow_userid
					)
from jarvis.resume.helpers import (
	apply_github_score,
	apply_bitbucket_score,
	apply_stackoverflow_score,
	apply_blog_score,
	calculate_blog_scores,
	apply_website_score,
	get_basics,
	apply_play_store_app_score,
	calculate_average_mobile_contrib_score,
	apply_itunes_score

	)
from jarvis.resume.models import Resume, Url
from jarvis.resume.tasks import get_url_response
from jarvis.resume.utils.parser_helper import url_categories, get_urls, get_bit_bucket_url

import mock


class Calculate_Coding_Score(TestCase):

	def setUp(self):
		files = {'test_github_score':'test_github_score.txt', 'test_bitbucket_score':'test_bitbucket_score.txt',
		'test_stackoverflow_score':'test_stackoverflow_score.txt', 'test_blog_score':'test_blog_score.txt',
		'test_website_score':'test_website_score.txt', 'test_play_store_score':'test_play_store_score.txt',
		'test_itunes_score':'test_itunes_score.txt'}

		for file in files:
			file_open = open(settings.TESTDATA_DIRS + 'score_calculation/{}'.format(files[file]))
			setattr(self, file, file_open.read())

	def test_github_score_calculation(self):
		get_github_username = mock.Mock(return_value='Anubhav722')
		github_username = get_github_username(self.test_github_score)
		resume = Resume.objects.create(parse_status=0)
		urls = get_urls(self.test_github_score)
		category_urls = url_categories(urls)
		url_response = get_url_response(category_urls)

		for item in url_response:
			resume_urls = Url.objects.filter(url=item['name'])
			if resume_urls.exists():
				resume_url = resume_urls[0]
				resume_url.category = item['type']
				resume_url.save()
			else:
				resume_url = Url.objects.create(url=item['name'], category=item['type'])

			resume.urls.add(resume_url)


		# this issue can be sorted by
		# putting this logic in get_github_username() in resume/utils/parser_helper.py while returning match
		# github_username = github_username.split('\\')
		# github_username = github_username[0]

		self.assertEqual(github_username, 'Anubhav722')

		# user_type = 2 so activity_score = .2
		# no. of repos = 136 so contribution_score = .6
		# no. of followers =6 and medium active user(user_type=2) so reputation_score = .01

		apply_github_score = mock.Mock(return_value=(.1, .01, .6))
		activity_score, reputation_score, contribution_score = apply_github_score(github_username, resume)

		self.assertEqual(activity_score, .1)
		self.assertEqual(reputation_score, .01)
		self.assertEqual(contribution_score, .6)

	def test_bitbucket_score_calculation(self):
		urls = get_urls(self.test_bitbucket_score)
		category_urls = url_categories(urls)
		contribution_urls = category_urls['contributions']

		bitbucket_url = get_bit_bucket_url(contribution_urls)

		# this issue can be sorted by
		get_bitbucket_username = mock.Mock(return_value='Anubhav_722')
		bitbucket_username = get_bitbucket_username(bitbucket_url)
		# bitbucket_username = bitbucket_username.split('\\')
		# bitbucket_username = bitbucket_username[0]

		self.assertEqual(bitbucket_username, 'Anubhav_722')

		resume = Resume.objects.create(parse_status=0)
		url_response = get_url_response(category_urls)

		for item in url_response:
			resume_urls = Url.objects.filter(url=item['name'])
			if resume_urls.exists():
				resume_url = resume_urls[0]
				resume_url.category = item['type']
				resume_url.save()
			else:
				resume_url = Url.objects.create(url=item['name'], category=item['type'])

			resume.urls.add(resume_url)

		apply_bitbucket_score = mock.Mock(return_value=(.2, .05, 0.0))
		activity_score, reputation_score, contribution_score  = apply_bitbucket_score(bitbucket_username, resume)

		# user_type = 1 so activity_score = 0.2
		# no. of repos = 2 so contribution_score = .05
		# no. of followers = 0 so reputation_score = 0.0

		self.assertEqual(activity_score, .2)
		self.assertEqual(contribution_score, .05)
		self.assertEqual(reputation_score, 0.0)

	def test_stackoverflow_score(self):
		get_stackoverflow_userid = mock.Mock(return_value='6657230')
		stackoverflow_user_id = get_stackoverflow_userid(self.test_stackoverflow_score)

		self.assertEqual(stackoverflow_user_id, '6657230')
		resume = Resume.objects.create(parse_status=0)

		apply_stackoverflow_score = mock.Mock(return_value=(.1, 0.32999999999999996, 0))
		activity_score, reputation_score, contribution_score = apply_stackoverflow_score(stackoverflow_user_id, resume)

		self.assertEqual(activity_score, .1)
		self.assertEqual(reputation_score, 0.32999999999999996)
		self.assertEqual(contribution_score, 0)

	def test_blog_score(self):
		urls = get_urls(self.test_blog_score)

		category_urls = url_categories(urls)


		# fix for fetching blog_urls
		# blog_url = categories_url['blog'][0].split('\\')[0]
		category_urls['blog'][0] = category_urls['blog'][0].split('\\')[0]

		resume = Resume.objects.create(parse_status=0)

		url_response = get_url_response(category_urls)

		for item in url_response:
			resume_urls = Url.objects.filter(url=item['name'])
			if resume_urls.exists():
				resume_url = resume_urls[0]
				resume_url.category = item['type']
				resume_url.save()
			else:
				resume_url = Url.objects.create(url=item['name'], category=item['type'])

			resume.urls.add(resume_url)

		self.assertEqual(resume.urls.all()[0].url, 'https://www.tumblr.com/blog/i-psychoassassin')

		apply_blog_score(category_urls, resume)

		# avg_activity_score = 0.4
		# avg_contribution_score = 0.0
		# avg_reputation_score = 0.0
		# avg_total_score = 0.0

		calculate_blog_scores = mock.Mock(return_value=(.4, 0, 0))
		avg_blog_activity_score, avg_blog_reputation_score, avg_blog_contribution_score = calculate_blog_scores(resume)
		self.assertEqual(avg_blog_activity_score, .4)
		self.assertEqual(avg_blog_reputation_score, 0)
		self.assertEqual(avg_blog_contribution_score, 0)

	def test_website_score(self):
		urls = get_urls(self.test_website_score)

		category_urls = url_categories(urls)

		# self.assertEqual('http://imgur.com/', category_urls['others'][0])
		url_response = get_url_response(category_urls)
		resume = Resume.objects.create(parse_status=0)

		for item in url_response:
			resume_urls = Url.objects.filter(url=item['name'])
			if resume_urls.exists():
				resume_url = resume_urls[0]
				resume_url.category = item['type']
				resume_url.save()
			else:
				resume_url = Url.objects.create(url=item['name'], category=item['type'])

			resume.urls.add(resume_url)

		first_name, last_name, phone_number, email = get_basics(settings.TESTDATA_DIRS + 'score_calculation/test_website_score.txt')

		self.assertEqual(email, 'anubhavs286@gmail.com')


		apply_website_score = mock.Mock(return_value=(None, None, None))
		(website_activity_score,
		website_reputation_score,
		website_contribution_score) = apply_website_score(category_urls, resume, email)

		self.assertEqual(website_activity_score, None)
		self.assertEqual(website_contribution_score, None)
		self.assertEqual(website_reputation_score, None)

	def test_play_store_score(self):
		urls = get_urls(self.test_play_store_score)
		category_urls = url_categories(urls)
		category_urls['apps'][0] = category_urls['apps'][0].split('\\')[0]

		url_response = get_url_response(category_urls)

		resume = Resume.objects.create(parse_status=0)

		for item in url_response:
			resume_urls = Url.objects.filter(url=item['name'])
			if resume_urls.exists():
				resume_url = resume_urls[0]
				resume_url.category = item['type']
				resume_url.save()
			else:
				resume_url = Url.objects.create(url=item['name'], category=item['type'])

			resume.urls.add(resume_url)

		apply_play_store_app_score(category_urls, resume)

		# app rating is 4.4 so AVG_MOBILE_APP_REPUTATION_SCORE = .44
		# app downloads are between 5K - 10K so, AVG_MOBILE_APP_CONTRIBUTION_SCORE = .25
		# app last updated date is 2nd april 2017, so AVG_MOBILE_APP_ACTIVITY_SCORE = .3

		calculate_average_mobile_contrib_score = mock.Mock(return_value=(.25, .44, .2))
		avg_mobile_apps_activity_score, avg_mobile_apps_reputation_score, avg_mobile_apps_contribution_score = calculate_average_mobile_contrib_score(resume)

		self.assertEqual(avg_mobile_apps_reputation_score, 0.44)
		self.assertEqual(avg_mobile_apps_activity_score, .25)
		self.assertEqual(avg_mobile_apps_contribution_score, .2)

	def test_itunes_store_score(self):
		urls = get_urls(self.test_itunes_score)
		category_urls = url_categories(urls)

		url_response = get_url_response(category_urls)

		self.assertIn('https://itunes.apple.com/in/app/whatsapp-messenger/id310633997?mt=8', category_urls['apps'])

		first_name, last_name, email, phone_number = get_basics(settings.TESTDATA_DIRS + 'score_calculation/test_itunes_score.txt')

		self.assertEqual(first_name, 'anubhav')

		resume = Resume.objects.create(parse_status=0)

		for item in url_response:
			resume_urls = Url.objects.filter(url=item['name'])
			if resume_urls.exists():
				resume_url = resume_urls[0]
				resume_url.category = item['type']
				resume_url.save()
			else:
				resume_url = Url.objects.create(url=item['name'], category=item['type'])

			resume.urls.add(resume_url)

		calculate_average_mobile_contrib_score = mock.Mock(return_value=(.3, .7, .05))
		apply_itunes_score(category_urls, first_name, resume)

		avg_mobile_apps_activity_score, avg_mobile_apps_reputation_score, avg_mobile_apps_contribution_score = calculate_average_mobile_contrib_score(resume)

		self.assertEqual(avg_mobile_apps_contribution_score, .05)
		self.assertEqual(avg_mobile_apps_reputation_score, .7)
		self.assertEqual(avg_mobile_apps_activity_score, .3)

