from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import default_storage

from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from rest_framework import status

from jarvis.resume.views import (Resume as Res,
	GetUploadLimitView,
	TrialUserView,
	ValidateTrialUser,
	TopCompaniesList,
	SkillsSuggestion,
	ResumeDetailView,
	TrialResumeDetailView,
	ResumeFilterDetailView,
	SampleResumeView,
	ResumeParseInternal,
	ResumeSyncView,
	AcademicDegreeList,
	SampleResumeDetailView,
	ResumeFilter)

from jarvis.resume.models import Skill, TrialUser, Company, Resume
from jarvis.resume.utils.parser_helper import get_sim_hash_for_resume_content
from jarvis.resume.utils.extractor import get_text

from jarvis.resume.tasks import parse_resume

import shutil
import json
from uuid import UUID, uuid4

class ResumeUploadTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_resume_upload_without_token(self):
		request = self.factory.post('/api/resumes/')

		request.user = self.user

		response = Res.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_resume_upload_with_token_without_filling_out_fields(self):

		request = self.factory.post('/api/resumes')
		force_authenticate(request, user=self.user, token=self.user.auth_token)

		response = Res.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.content, '{"skills": ["This field is required."], "file": ["This field is required."]}')


	def test_resume_upload_with_token_and_fields(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		data = 'python, django, flask'
		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')

		request = self.factory.post('/api/resumes', {'skills':data, 'file':files})
		force_authenticate(request, user=self.user, token=self.user.auth_token)

		response = Res.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		json_status = json.loads(response.content)
		self.assertEqual(json_status['status'], 'processing')

	# def test_generation_of_client_key_and_client_secret(self):

class GetUploadLimitViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_get_resume_upload_limit(self):
		request = self.factory.get('/api/resumes/limit')
		force_authenticate(request, user=self.user, token=self.user.auth_token)

		response = GetUploadLimitView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['upload_remaining'], 20)

		# Uploading a resume and then making request to 'limits' url.
		data = 'python, django, flask'
		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		request = self.factory.post('/api/resumes', {'skills':data, 'file':files})
		force_authenticate(request, user=self.user, token=self.user.auth_token)
		response = Res.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		request = self.factory.get('/api/resumes/limit')
		force_authenticate(request, user=self.user, token=self.user.auth_token)

		response = GetUploadLimitView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['upload_remaining'], 19)

class TrialUserViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_trial_user_resume_upload_without_providing_email(self):
		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')

		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files})

		response = TrialUserView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data, {'email_address': ['This field is required.']})

	def test_trial_user_resume_upload_with_email(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		trialuser_count = TrialUser.objects.count()

		self.assertEqual(trialuser_count, 0)

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')

		email_address = 'anubhavs286@gmail.com'
		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files, 'email_address':email_address})

		response = TrialUserView.as_view()(request)

		trialuser_count = TrialUser.objects.count()
		trialuser = TrialUser.objects.first()

		self.assertEqual(trialuser_count, 1)
		self.assertEqual(trialuser.email_address, 'anubhavs286@gmail.com')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['status'], 'processing')

class ValidateTrialUserTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_with_trial_user_email_which_has_not_reached_threshold(self):
		email = 'anubhavs286@gmail.com'

		request = self.factory.get('/api/resumes/trial-user/validate/?email={}'.format(email))

		response = ValidateTrialUser.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['status'], 'success')
		self.assertEqual(response.data['message'], 'anubhavs286@gmail.com is valid.')

	def test_with_user_trial_email_which_has_reached_threshold(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		email_address = 'anubhavs286@gmail.com'
		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files, 'email_address':email_address})

		response = TrialUserView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['status'], 'processing')

		email = 'anubhavs286@gmail.com'

		request = self.factory.get('/api/resumes/trial-user/validate/?email={}'.format(email))

		response = ValidateTrialUser.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(response.data['status'], 'failure')
		self.assertEqual(response.data['message'], 'This email has already been used for the trial version.')

	def test_with_trial_user_email_present_in_DESPOSABLE_EMAIL_DOMAINS(self):
		email = 'anubhavs286@027168.com'

		request = self.factory.get('/api/resumes/trial-user/validate/?email={}'.format(email))

		response = ValidateTrialUser.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(response.data['status'], 'failure')
		self.assertEqual(response.data['message'], 'Please use a valid email address.')

class TopCompaniesListView(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')
		Company.objects.create(name='Google', rank=1)
		Company.objects.create(name='Facebook', rank=3)
		Company.objects.create(name='Quora', rank=2)

	def test_order_list_of_companies_according_to_rank(self):
		request = self.factory.get('api/resumes/companies/top')

		response = TopCompaniesList.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data[0]['name'], 'Google')
		self.assertEqual(response.data[1]['name'], 'Quora')
		self.assertEqual(response.data[2]['name'], 'Facebook')

class SkillsSuggestionTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_when_no_skill_is_provided_in_query_param(self):
		request = self.factory.get('api/resumes/skill-suggestion/')

		response = SkillsSuggestion.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['result'], '')

	def test_when_skill_is_provided_in_query_param(self):
		request = self.factory.get('api/resumes/skill-suggestion/?q=python')

		response = SkillsSuggestion.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['result'], ['flask', 'python', 'pyramid', 'tornado', 'django'])

		request = self.factory.get('api/resumes/skill-suggestion/?q=javascript')
		response = SkillsSuggestion.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('react-js', response.data['result'])

class ResumeDetailViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')
		Resume.objects.create(parse_status=0)

	def test_resume_details_endpoint(self):
		resume = Resume.objects.first()
		request = self.factory.get('/api/resumes/')

		response = ResumeDetailView.as_view()(request, id=resume.id)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_trial_user_resume_details_are_filtered(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')

		email_address = 'anubhavs286@gmail.com'
		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files, 'email_address':email_address})

		response = TrialUserView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		resume = Resume.objects.first()
		request = self.factory.get('/api/resumes/')
		response = ResumeDetailView.as_view()(request, id=resume.id)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TrialResumeDetailViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')
		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		email_address = 'anubhavs286@gmail.com'
		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files, 'email_address':email_address})

		response = TrialUserView.as_view()(request)

	def test_trial_users_resume_details(self):
		request = self.factory.get('/api/resumes/trial/')
		resume = Resume.objects.first()

		response = TrialResumeDetailView.as_view()(request, id=resume.id)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

class ResumeFilterViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_resume_filter_view_without_providing_ids(self):
		request = self.factory.post('/api/resumes/filter/', HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
		force_authenticate(request, user=self.user)

		response = ResumeFilter.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('count'), 0)
		self.assertEqual(response.data.get('next'), None)


	def test_resume_filter_view_with_ids(self):
		resume_1 = Resume.objects.create(parse_status=0)
		resume_2 = Resume.objects.create(parse_status=0)
		data = {'ids':[resume_1.id, resume_2.id],}
		# data = json.loads(data)
		request = self.factory.post('/api/resumes/filter/', data, HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
		force_authenticate(request, user=self.user)

		response = ResumeFilter.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('count'), 2)

	def test_resume_filter_view_with_ids_and_skills_as_params(self):
		resume = Resume.objects.create(parse_status=0)
		request = self.factory.post('/api/resumes/filter/?skills=python', {'ids':resume.id,}, HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
		force_authenticate(request, user=self.user)

		response = ResumeFilter.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get('count'), 1)


# class ResumeFilterDetailViewTest(TestCase):

# 	def setUp(self):
# 		self.factory = APIRequestFactory()
# 		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')


# 	def test_resume_filter_detail_view(self):
# 		resume = Resume.objects.create(parse_status=0)
# 		request = self.factory.get('/api/resumes/filter/{}'.format(resume.id))#, kwargs={'id':resume.id})

# 		kwargs = {'id':resume.id}
# 		response = ResumeFilterDetailView.as_view()(request, kwargs={'id': resume.id})

# 		self.assertEqual(response.status_code, status.HTTP_200_OK)


class SampleResumeViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_sample_resume_response_for_existing_trial_user_email(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		email_address = 'anubhavs286@gmail.com'
		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files, 'email_address':email_address})

		response = TrialUserView.as_view()(request)

		skills = 'python, hadoop'
		email = email_address
		file = 'nda.pdf'
		request = self.factory.post('/api/resumes/sample', {'skills':skills, 'email':email, 'file':file})

		response = SampleResumeView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['message'], 'Email Address already used. Try with another one.')

	def test_sample_resume_response_when_data_is_not_present(self):
		skills = 'python, hadoop'
		email = 'anubhavs286@gmail.com'
		file = 'nda.pdf'

		request = self.factory.post('/api/resumes/sample', {'skills':skills, 'email':email, 'file':file})

		response = SampleResumeView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(response.data['message'], 'Sample data not found.')


	def test_sample_resume_response_when_data_is_present(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		email_address = 'sample@aircto.com'
		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files, 'email_address':email_address})
		response = TrialUserView.as_view()(request)

		resume = Resume.objects.first()
		resume.file_name = 'nda.pdf'
		resume.save()

		skills = 'python, hadoop'
		email = 'anubhavs286@gmail.com'
		file = 'nda.pdf'

		request = self.factory.post('/api/resumes/sample', {'skills':skills, 'email':email, 'file':file})
		response = SampleResumeView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['status'], 'processing')


class ResumeParseInternalTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')


	def test_parsed_response_of_view(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')

		request = self.factory.post('/api/resumes/internal', {'file':files})
		force_authenticate(request, user = self.user)

		response = ResumeParseInternal.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['first_name'], 'anubhav')
		self.assertEqual(response.data['email'], 'anubhavs286@gmail.com')


class ResumeSyncViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_resume_sync_view_response_with_correct_uuid(self):
		resume = Resume.objects.create(parse_status=0)
		request = self.factory.post('/api/resumes/sync', {'resume_id':resume.id})
		force_authenticate(request, user=self.user, token='self.user.auth_token')

		response = ResumeSyncView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['message'], 'success')

	def test_resume_sync_view_response_with_incorrect_uuid(self):
		request = self.factory.post('/api/resumes/sync', {'resume_id': 'asdasd'})
		force_authenticate(request, user=self.user, token='self.user.user_token')

		response = ResumeSyncView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['message'], 'not a valid uuid')


class AcademicDegreeListTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()

	def test_view_response_and_no_of_disciplines(self):
		request = self.factory.get('/api/resumes/degrees')

		response = AcademicDegreeList.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 14)


class SampleResumeDetailViewTest(TestCase):

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(username='anubhav', email='anubhav@gmail.com', password='password123')

	def test_sample_resume_detail_view(self):
		try:
			shutil.rmtree(settings.MEDIA_ROOT)
		except OSError:
			pass

		files = open(settings.TESTDATA_DIRS + 'view_tests/nda.pdf', 'rb')
		email_address = 'sample@aircto.com'
		request = self.factory.post('/api/resumes/trial', {'skills':'python, django', 'file':files, 'email_address':email_address})
		response = TrialUserView.as_view()(request)

		resume = Resume.objects.first()
		resume.file_name = 'nda.pdf'
		resume.save()

		skills = 'python, hadoop'
		email = 'anubhavs286@gmail.com'
		file = 'nda.pdf'

		request = self.factory.post('/api/resumes/sample', {'skills':skills, 'email':email, 'file':file})
		response = SampleResumeView.as_view()(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['status'], 'processing')

		request = self.factory.get('/api/resumes/sample/')
		response = SampleResumeDetailView.as_view()(request, id = response.data['resume_id'])

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['file_name'], 'nda.pdf')

