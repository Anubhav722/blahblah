from jarvis.resume.utils.ranking.bit_bucket import BitBucketScore
from jarvis.resume.utils.ranking.github import GitHubScore
from jarvis.resume.utils.ranking.blog import BlogScore, get_url_details
from jarvis.resume.utils.ranking.stackoverflow import StackOverflowScore
from jarvis.resume.utils.ranking.itunes import ItunesScore
from jarvis.resume.utils.ranking.play_store_app import PlayStoreAppRating
import mock
import datetime
from requests.models import Response
from django.test import TestCase

# Test Data Response
from .test_data.stakoverflow_response import stackoverflow_response
from .test_data.github_response import github_response
from .test_data.bit_bucket_response import bit_bucket_response


class TestStackOverflowAlgorithm(TestCase):
    """
    Test StackOverflow Algorithm
    """
    def setUp(self):

        self.response = Response()
        self.response.json = mock.MagicMock(return_value=stackoverflow_response)
        self.user_details = self.response.json()
        today_date = datetime.date.today()
        self.response.status_code = 200
        test_used_id = 2231236
        self.months_passed = (today_date - self.user_details['account_creation_date']).days / float(30)
        self.days_passed = (today_date - self.user_details['last_access_date']).days
        self.stackOverflowScore = StackOverflowScore(test_used_id)
        self.reputation_change_month = self.user_details['reputation_change_month']
        self.stackOverflowScore.answer_score = 0.07
        self.stackOverflowScore.acceptance_score = 0.07
        self.stackOverflowScore._user_details = stackoverflow_response
        self.stackOverflowScore.user_type = 5
        self.stackOverflowScore.total_no_of_questions = self.user_details['total_no_questions']
        self.stackOverflowScore.total_no_of_unaccepted_questions = self.user_details['total_unaccepted_questions']
        self.stackOverflowScore.total_no_of_unanswered_questions = self.user_details['total_unanswered_questions']
        self.stackOverflowScore._answer_rate = (self.stackOverflowScore.total_no_of_unanswered_questions / float(self.stackOverflowScore.total_no_of_questions)) * 100
        self.stackOverflowScore._acceptance_rate = (self.stackOverflowScore.total_no_of_unaccepted_questions / float(self.stackOverflowScore.total_no_of_questions)) * 100

    def test_type_of_user(self):
        """Test StackOveflow type of user"""
        dummy_user_type = 5
        type_of_user = self.stackOverflowScore._type_of_user(self.months_passed, self.days_passed,
                                                             self.reputation_change_month)
        self.assertEqual(type_of_user, dummy_user_type)

    def test_answer_score(self):
        """Test StackOverflow Answer Score"""
        dummy_answer_score = 0.07
        total_no_of_questions = self.user_details['total_no_questions']
        total_no_of_unanswered_questions = self.user_details['total_unanswered_questions']
        answer_score = self.stackOverflowScore._answer_score(total_no_of_questions, total_no_of_unanswered_questions)
        self.assertEqual(answer_score, dummy_answer_score)

    def test_acceptance_score(self):
        """Test StackOverflow Acceptance Score"""
        dummy_acceptance_score = 0.07
        total_no_of_questions = self.user_details['total_no_questions']
        total_no_of_unaccepted_questions = self.user_details['total_unaccepted_questions']
        acceptance_score = self.stackOverflowScore._acceptance_score(total_no_of_questions,
                                                                     total_no_of_unaccepted_questions)
        self.assertEqual(acceptance_score, dummy_acceptance_score)

    def test_user_reputation_score(self):
        """Test StackOverflow User Reputation Score"""
        dummy_user_reputation_score = 0.18
        total_reputation = self.user_details['reputation']
        type_of_user = 5
        user_reputation_score = self.stackOverflowScore._user_reputation_score(total_reputation, type_of_user)
        self.assertEqual(user_reputation_score, dummy_user_reputation_score)

    def test_user_badges_score(self):
        """Test StackOverflow Badges Score"""
        dummy_user_badges_score = 0.3
        type_of_user = 5
        gold_badges = self.user_details['gold_badges_count']
        silver_badges = self.user_details['silver_badges_count']
        bronze_badges = self.user_details['bronze_badges_count']
        user_badges_score = self.stackOverflowScore._user_badges_score(gold_badges, silver_badges, bronze_badges,
                                                                       type_of_user)
        self.assertEqual(user_badges_score, dummy_user_badges_score)

    def test_get_activity_score(self):
        """Test StackOverflow Activity Score"""
        dummy_activity_score = 0.1
        activity_score = self.stackOverflowScore.get_activity_score()
        self.assertEqual(activity_score, dummy_activity_score)

    def test_get_contribution_score(self):
        """Test StackOverflow Contribution Score"""
        dummy_contribution_score = 0.14
        contribution_score = self.stackOverflowScore.get_contribution_score()
        self.assertEqual(contribution_score, dummy_contribution_score)

    def test_get_reputation_score(self):
        """Test StackOverflow Reputation Score"""
        dummy_reputation_score = 0
        reputation_score = self.stackOverflowScore.get_reputation_score()
        self.assertEqual(reputation_score, dummy_reputation_score)


class TestGitHubAlgorithm(TestCase):
    """
    Test for GitHub Algorithm
    """
    def setUp(self):
        self.response = Response()
        self.response.json = mock.MagicMock(return_value=github_response)
        self.user_details = self.response.json()
        today_date = datetime.date.today()
        account_creation_date = self.user_details['account_created_at'].date()
        account_updated_at = self.user_details['last_updated_at'].date()
        self.months_passed = (today_date - account_creation_date).days / float(30)
        self.days_passed = (today_date - account_updated_at).days
        self.githubScore = GitHubScore('yamanahlawat')
        self.githubScore._user_details = github_response
        self.githubScore.user_type = 4
        self.githubScore.total_no_of_repos = 10
        self.githubScore.no_of_followers = 0

    def test_type_of_user(self):
        """Test GitHub Type of user"""
        dummy_type_of_user = 5
        type_of_user = self.githubScore._type_of_user(self.months_passed, self.days_passed)
        self.assertEqual(type_of_user, dummy_type_of_user)

    def test_get_activity_score(self):
        """Test GitHub Activity Score"""
        dummy_activity_score = 0.2
        activity_score = self.githubScore.get_activity_score()
        self.assertEqual(activity_score, dummy_activity_score)

    def test_get_contribution_score(self):
        """Test GitHub Contribution Score"""
        dummy_contribution_score = 0.05
        contribution_score = self.githubScore.get_contribution_score()
        self.assertEqual(contribution_score, dummy_contribution_score)

    def test_get_reputation_score(self):
        """Test GitHub Reputation Score"""
        dummy_reputation_score = 0
        reputation_score = self.githubScore.get_reputation_score()
        self.assertEqual(reputation_score, dummy_reputation_score)


class TestBitBucketAlgorithm(TestCase):
    """
    Test for BitBucket Algorithm
    """
    def setUp(self):
        self.response = Response()
        self.response.json = mock.MagicMock(return_value=bit_bucket_response)
        self.user_details = self.response.json()
        self.bit_bucket_score = BitBucketScore('jespern')
        self.bit_bucket_score._user_details = bit_bucket_response
        today_date = datetime.date.today()
        self.account_created_at = self.user_details['account_created_at']
        self.months_passed = (today_date - self.account_created_at).days / float(30)
        self.bit_bucket_score.user_type = 2
        self.bit_bucket_score.total_no_of_repos = 56
        self.bit_bucket_score.no_of_followers = 255

    def test_get_activity_score(self):
        """
        Test Bit Bucket activity score
        """
        dummy_activity_score = 0.2
        activity_score = self.bit_bucket_score.get_activity_score()
        self.assertEqual(activity_score, dummy_activity_score)

    def test_get_contribution_score(self):
        """
        Test Bit Bucket Contribution Score
        """
        dummy_contribution_score = 0.5
        contribution_score = self.bit_bucket_score.get_contribution_score()
        self.assertEqual(contribution_score, dummy_contribution_score)

    def test_get_reputation_score(self):
        """
        Test Bit Bucket Reputation Score
        """
        dummy_reputation_score = 0.2
        reputation_score = self.bit_bucket_score.get_reputation_score()
        self.assertEqual(reputation_score, dummy_reputation_score)

    def test_type_of_user(self):
        """
        Test Bit Bucket Type of user
        """
        dummy_type_of_user = 2
        type_of_user = self.bit_bucket_score._type_of_user(self.months_passed)
        self.assertEqual(type_of_user, dummy_type_of_user)


class TestItunesAlgorithm(TestCase):
    """
    Test for Itunes Algorithm
    """

    def setUp(self):
        self.url = 'https://itunes.apple.com/in/app/adobe-acrobat-reader-annotate-scan-send-pdfs/id469337564?mt=8'
        self.developer_name = 'yamanahlawat'
        self.itunes_score = ItunesScore(self.url, self.developer_name)

    def test_get_contribution_score(self):
        """Test Itunes Contribution Score"""
        dummy_contribution_score = 0.05
        contribution_score = self.itunes_score.get_contribution_score()
        self.assertEqual(contribution_score, dummy_contribution_score)

    def test_get_activity_score(self):
        """Test Itunes Activity Score"""
        dummy_activity_score = 0.3
        activity_score = self.itunes_score.get_activity_score()
        self.assertEqual(activity_score, dummy_activity_score)

    def test_get_reputation_score(self):
        """Test Itunes Reputation Score"""
        dummy_reputation_score = 0.42500000000000004
        reputation_score = self.itunes_score.get_reputation_score()
        self.assertEqual(dummy_reputation_score, reputation_score)

    def test_get_total_score(self):
        """Test Itunes Total Score"""
        dummy_total_score = 0.78
        total_score = self.itunes_score.get_total_score()
        self.assertEqual(dummy_total_score, total_score)


class TestBlogAlgorithm(TestCase):
    """Test For Blog Algorithm"""
    def setUp(self):
        self.url = 'http://medium.com/@aatifh'
        self.blog_details = get_url_details(self.url)
        self.blog_score = BlogScore(self.blog_details)

    def test_get_contribution_score(self):
        """Test Blog Contribution Score"""
        dummy_contribution_score = 0.16
        contribution_score = self.blog_score.get_contribution_score()
        self.assertEqual(contribution_score, dummy_contribution_score)

    def test_get_activity_score(self):
        """Test Blog Activity Score"""
        dummy_activity_score = 0.4
        activity_score = self.blog_score.get_activity_score()
        self.assertEqual(activity_score, dummy_activity_score)

    def test_get_reputation_score(self):
        """Test Blog Repuatation Score"""
        dummy_reputation_score = 0.2
        reputation_score = self.blog_score.get_reputation_score()
        self.assertEqual(dummy_reputation_score, reputation_score)

    def test_get_total_score(self):
        """Test Blog Total Score"""
        dummy_total_score = 0.76
        total_score = self.blog_score.get_total_score()
        self.assertEqual(dummy_total_score, total_score)


class TestPlayStoreAlgorithm(TestCase):
    """Test for Play Store Algorithm"""
    def setUp(self):
        self.url = 'https://play.google.com/store/apps/details?id=com.whatsapp'
        self.android_score = PlayStoreAppRating(self.url)

    def test_get_contribution_score(self):
        """Test Android Contribution Score"""
        dummy_contribution_score = 0.25
        contribution_score = self.android_score.get_contribution_score()
        self.assertEqual(contribution_score, dummy_contribution_score)

    def test_get_activity_score(self):
        """Test Android Activity Score"""
        dummy_activity_score = 0.25
        activity_score = self.android_score.get_activity_score()
        self.assertEqual(activity_score, dummy_activity_score)

    def test_get_reputation_score(self):
        """Test Android Reputation Score"""
        dummy_reputation_score = 0.44000000000000006
        reputation_score = self.android_score.get_reputation_score()
        self.assertEqual(dummy_reputation_score, reputation_score)

    def test_get_total_score(self):
        """Test Android Total Score"""
        dummy_total_score = 0.94
        total_score = self.android_score.get_total_score()
        self.assertEqual(dummy_total_score, total_score)

