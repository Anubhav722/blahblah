from django.test import TestCase
from jarvis.resume.models import Url, Resume, Skill
from .factories import (UrlFactory,  ScoreFactory, ResumeFactory, SkillFactory, BitBucketFactory,
                        StackOverflowFactory, GitHubFactory, BlogFactory, MobileAppFactory, WebsiteFactory)
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from faker import Faker
import random
import pytz

# Declaration
fake = Faker()


class UrlTest(TestCase):
    """Test Case for Url Model"""
    def test_str(self):
        dummy_url = fake.url()
        url = UrlFactory(url=dummy_url)
        self.assertEqual(url.__unicode__(), dummy_url)

    def test_categories(self):
        category = UrlFactory(category='social')
        self.assertEqual(category.category, 'social')

    def test_url(self):
        dummy_url = fake.url()
        url = UrlFactory(url=dummy_url)
        self.assertEqual(url.url, dummy_url)

    def test_ordering(self):
        dummy_url = fake.url()
        u1, u2 = UrlFactory.create_batch(2)
        url_instance = Url.objects.all()
        self.assertEqual(url_instance[1].id, u1.id)
        u1.url = dummy_url
        u1.save()
        url_instance = Url.objects.all()
        self.assertEqual(url_instance[1].id, u1.id)


class ScoreTest(TestCase):
    """Test Case for Score Model"""
    def test_score_type(self):
        type_test = ScoreFactory(type=0)
        self.assertEqual(type_test.type, 0)


class SkillTest(TestCase):
    """Test Case for skill Model"""
    def test_skill_name(self):
        dummy_skill = fake.first_name().lower()
        name_test = SkillFactory(name=dummy_skill)
        self.assertEqual(name_test.name, dummy_skill)

    def test_slug(self):
        dummy_slug = fake.slug()
        slug_test = Skill(slug=dummy_slug)
        self.assertEqual(slug_test.slug, dummy_slug)


class ResumeTest(TestCase):
    """ Test for Resume Model """
    def test_parse_status(self):
        parse_status_test = ResumeFactory(parse_status=1)
        self.assertEqual(parse_status_test.parse_status, 1)

    def test_duplicate_id_are_invalid(self):
        try:
            test_id = Resume.objects.create().id
            with self.assertRaises(ValidationError, IntegrityError):
                user = Resume(id=test_id, parse_status=0)
                user.full_clean()
        except IntegrityError:
            return

    def test_created_duplicate_resume_id(self):
        try:
            uid = Resume.objects.create().id
            self.assertRaises(IntegrityError, ValidationError, Resume.objects.create, id=uid)
            user = Resume(id=uid, parse_status=0)
            user.full_clean()
        except IntegrityError:
            return

    def test_file_name(self):
        dummy_file_name = fake.name() + '.pdf'
        test_file_name = ResumeFactory(file_name=dummy_file_name)
        self.assertEqual(test_file_name.file_name, dummy_file_name)

    def test_hash(self):
        dummy_text = fake.text()
        hash_test = ResumeFactory(content_hash=dummy_text)
        self.assertEqual(hash_test.content_hash, dummy_text)

    def test_content(self):
        dummy_text = fake.text()
        content_test = ResumeFactory(content=dummy_text)
        self.assertEqual(content_test.content, dummy_text)

    def test_first_name(self):
        dummy_first_name = fake.first_name()
        first_name = ResumeFactory(first_name=dummy_first_name)
        self.assertEqual(first_name.first_name, dummy_first_name)

    def test_last_name(self):
        dummy_last_name = fake.last_name()
        last_name = ResumeFactory(last_name=dummy_last_name)
        self.assertEqual(last_name.last_name, dummy_last_name)

    def test_email(self):
        dummy_email = fake.email()
        email = ResumeFactory(email=dummy_email)
        self.assertEqual(email.email, dummy_email)

    def test_phone_number(self):
        dummy_phone_number = str(fake.random_number(10))
        phone_number = ResumeFactory(phone_number=dummy_phone_number)
        self.assertEqual(phone_number.phone_number, dummy_phone_number)

    def test_str(self):
        dummy_id = fake.uuid4()
        resume_id = ResumeFactory(id=dummy_id)
        self.assertEqual(str(resume_id), "%s" % resume_id)

    def test_ordering(self):
        dummy_first_name = fake.first_name()
        r1, r2 = ResumeFactory.create_batch(2)
        resume_instance = Resume.objects.all()
        self.assertEqual(str(resume_instance[0].id), r1.id)
        r1.first_name = dummy_first_name
        r1.save()
        resume_instance = Resume.objects.all()
        self.assertEqual(str(resume_instance[0].id), r1.id)


class BitBucketTest(TestCase):
    """Test for BitBucketUser Model"""

    def test_user_name(self):
        dummy_user_name = fake.first_name().lower()
        user_name = BitBucketFactory(user_name=dummy_user_name)
        self.assertEqual(user_name.user_name, dummy_user_name)

    def test_display_name(self):
        dummy_display_name = fake.name()
        display_name = BitBucketFactory(display_name=dummy_display_name)
        self.assertEqual(display_name.display_name, dummy_display_name)

    def test_account_created_date(self):
        date_object = fake.date_time().replace(tzinfo=pytz.utc)
        account_created_at = BitBucketFactory(account_created_at=date_object)
        self.assertEqual(account_created_at.account_created_at, date_object)

    def test_total_no_public_repos(self):
        dummy_total_no_public_repos = random.randint(0, 100000)
        total_no_public_repos = BitBucketFactory(total_no_public_repos=dummy_total_no_public_repos)
        self.assertEqual(total_no_public_repos.total_no_public_repos, dummy_total_no_public_repos)

    def test_followers(self):
        dummy_followers = random.randint(0, 100000)
        followers = BitBucketFactory(followers=dummy_followers)
        self.assertEqual(followers.followers, dummy_followers)

    def test_following(self):
        dummy_following = 12345
        following = BitBucketFactory(following=dummy_following)
        self.assertEqual(following.following, dummy_following)

    def test_blog_url(self):
        dummy_blog_url = BitBucketFactory(blog_url='http://yamanahlawat.org/')
        self.assertEqual(dummy_blog_url.blog_url, 'http://yamanahlawat.org/')

    def test_profile_url(self):
        profile_url = BitBucketFactory(profile_url='http://aircto.com/')
        self.assertEqual(profile_url.profile_url, 'http://aircto.com/')

    def test_repositories_url(self):
        repositories_url = BitBucketFactory(repositories_url='http://launchyard.com/')
        self.assertEqual(repositories_url.repositories_url, 'http://launchyard.com/')

    def test_snippet_url(self):
        snippet_url = BitBucketFactory(snippet_url='http://google.com/')
        self.assertEqual(snippet_url.snippet_url, 'http://google.com/')

    def test_location(self):
        dummy_location = fake.state()
        location = BitBucketFactory(location=dummy_location)
        self.assertEqual(location.location, dummy_location)

    def test_reputation_score(self):
        dummy_reputation_score = random.random()
        reputation_score = BitBucketFactory(reputation_score=dummy_reputation_score)
        self.assertEqual(reputation_score.reputation_score, dummy_reputation_score)

    def test_contribution_score(self):
        dummy_contribution_score = random.random()
        contribution_score = BitBucketFactory(contribution_score=dummy_contribution_score)
        self.assertEqual(contribution_score.contribution_score, dummy_contribution_score)

    def test_activity_score(self):
        dummy_activity_score = random.random()
        activity_score = BitBucketFactory(activity_score=dummy_activity_score)
        self.assertEqual(activity_score.activity_score, dummy_activity_score)


class GitHubTest(TestCase):
    """Test for GitHub Model"""

    def test_user_id(self):
        dummy_user_id = random.randint(1, 100000)
        user_id = GitHubFactory(user_id=dummy_user_id)
        self.assertEqual(user_id.user_id, dummy_user_id)

    def test_user_name(self):
        dummy_user_name = fake.first_name().lower()
        user_name = GitHubFactory(user_name=dummy_user_name)
        self.assertEqual(user_name.user_name, dummy_user_name)

    def test_profile_name(self):
        dummy_profile_name = fake.name()
        profile_name = GitHubFactory(profile_name=dummy_profile_name)
        self.assertEqual(profile_name.profile_name, dummy_profile_name)

    def test_email(self):
        dummy_email = fake.email()
        email = GitHubFactory(email=dummy_email)
        self.assertEqual(email.email, dummy_email)

    def test_profile_url(self):
        # dummy_profile_url = 'http://github.com/yamanahlawat'
        profile_url = GitHubFactory(profile_url='http://github.com/yamanahlawat/')
        self.assertEqual(profile_url.profile_url, 'http://github.com/yamanahlawat/')

    def test_profile_image_url(self):
        # dummy_profile_image_url = 'http://imgurl.com/123'
        profile_image_url = GitHubFactory(profile_image_url='http://imgurl.com/123/')
        self.assertEqual(profile_image_url.profile_image_url, 'http://imgurl.com/123/')

    def test_gists_url(self):
        gists_url = GitHubFactory(gists_url='http://gist.github.com/yamanahlawat/')
        self.assertEqual(gists_url.gists_url, 'http://gist.github.com/yamanahlawat/')

    def test_location(self):
        dummy_location = fake.state()
        location = GitHubFactory(location=dummy_location)
        self.assertEqual(location.location, dummy_location)

    def test_blog_url(self):
        # dummy_blog_url = 'http://aircto.com/blog'
        profile_url = GitHubFactory(profile_url='http://aircto.com/blog/')
        self.assertEqual(profile_url.profile_url, 'http://aircto.com/blog/')

    def test_company(self):
        dummy_company = fake.company()
        company = GitHubFactory(company=dummy_company)
        self.assertEqual(company.company, dummy_company)

    def test_followers(self):
        dummy_followers = random.randint(0, 100000)
        followers = GitHubFactory(followers=dummy_followers)
        self.assertEqual(followers.followers, dummy_followers)

    def test_following(self):
        dummy_following = random.randint(0, 100000)
        following = GitHubFactory(following=dummy_following)
        self.assertEqual(following.following, dummy_following)

    def test_hireable(self):
        dummy_hireable = fake.boolean()
        hireable = GitHubFactory(hireable=dummy_hireable)
        self.assertEqual(hireable.hireable, dummy_hireable)

    def test_public_repos(self):
        dummy_public_repos = random.randint(0, 100000)
        public_repos = GitHubFactory(public_repos=dummy_public_repos)
        self.assertEqual(public_repos.public_repos, dummy_public_repos)

    def test_total_private_repos(self):
        dummy_total_private_repos = random.randint(0, 100000)
        total_private_repos = GitHubFactory(total_private_repos=dummy_total_private_repos)
        self.assertEqual(total_private_repos.total_private_repos, dummy_total_private_repos)

    def test_owned_private_repos(self):
        dummy_owned_private_repos = random.randint(0, 100000)
        owned_private_repos = GitHubFactory(owned_private_repos=dummy_owned_private_repos)
        self.assertEqual(owned_private_repos.owned_private_repos, dummy_owned_private_repos)

    def test_public_gists(self):
        dummy_public_gists = random.randint(0, 100000)
        public_gists = GitHubFactory(public_gists=dummy_public_gists)
        self.assertEqual(public_gists.public_gists, dummy_public_gists)

    def test_private_gists(self):
        dummy_private_gists = random.randint(0, 100000)
        private_gists = GitHubFactory(private_gists=dummy_private_gists)
        self.assertEqual(private_gists.private_gists, dummy_private_gists)

    def test_account_created_at(self):
        dummy_account_created_at = fake.date_time().replace(tzinfo=pytz.utc)
        account_created_at = GitHubFactory(account_created_at=dummy_account_created_at)
        self.assertEqual(account_created_at.account_created_at, dummy_account_created_at)

    def test_repo_updated_at(self):
        dummy_repo_updated_at = fake.date_time().replace(tzinfo=pytz.utc)
        repo_updated_at = GitHubFactory(repo_updated_at=dummy_repo_updated_at)
        self.assertEqual(repo_updated_at.repo_updated_at, dummy_repo_updated_at)

    def test_account_modified_at(self):
        dummy_account_modified_at = fake.date_time().replace(tzinfo=pytz.utc)
        account_modified_at = GitHubFactory(account_modified_at=dummy_account_modified_at)
        self.assertEqual(account_modified_at.account_modified_at, dummy_account_modified_at)

    def test_reputation_score(self):
        dummy_reputation_score = random.random()
        reputation_score = GitHubFactory(reputation_score=dummy_reputation_score)
        self.assertEqual(reputation_score.reputation_score, dummy_reputation_score)

    def test_contribution_score(self):
        dummy_contribution_score = random.random()
        contribution_score = GitHubFactory(contribution_score=dummy_contribution_score)
        self.assertEqual(contribution_score.contribution_score, dummy_contribution_score)

    def test_activity_score(self):
        dummy_activity_score = random.random()
        activity_score = GitHubFactory(activity_score=dummy_activity_score)
        self.assertEqual(activity_score.activity_score, dummy_activity_score)


class StackOverflowTest(TestCase):
    """Test for StackOverflow Model"""

    def test_user_id(self):
        dummy_user_id = random.randint(1, 100000)
        user_id = StackOverflowFactory(user_id=dummy_user_id)
        self.assertEqual(user_id.user_id, dummy_user_id)

    def test_profile_name(self):
        dummy_profile_name = fake.name()
        profile_name = StackOverflowFactory(profile_name=dummy_profile_name)
        self.assertEqual(profile_name.profile_name, dummy_profile_name)

    def test_location(self):
        dummy_location = fake.state()
        location = StackOverflowFactory(location=dummy_location)
        self.assertEqual(location.location, dummy_location)

    def test_profile_url(self):
        # dummy_profile_url = 'http://stackoverflow.com/users/2231236'
        profile_url = StackOverflowFactory(profile_url='http://stackoverflow.com/users/2231236/')
        self.assertEqual(profile_url.profile_url, 'http://stackoverflow.com/users/2231236/')

    def test_profile_image_url(self):
        # dummy_profile_image_url = 'http://stackoverflow.com/profile/234123'
        profile_url = StackOverflowFactory(profile_url='http://stackoverflow.com/profile/234123/')
        self.assertEqual(profile_url.profile_url, 'http://stackoverflow.com/profile/234123/')

    def test_reputation(self):
        dummy_reputation = random.randint(0, 100000)
        reputation = StackOverflowFactory(reputation=dummy_reputation)
        self.assertEqual(reputation.reputation, dummy_reputation)

    def test_gold_badges_count(self):
        dummy_gold_badges_count = random.randint(0, 100000)
        gold_badges_count = StackOverflowFactory(gold_badges_count=dummy_gold_badges_count)
        self.assertEqual(gold_badges_count.gold_badges_count, dummy_gold_badges_count)

    def test_silver_badges_count(self):
        dummy_silver_badges_count = random.randint(0, 100000)
        silver_badges_count = StackOverflowFactory(silver_badges_count=dummy_silver_badges_count)
        self.assertEqual(silver_badges_count.silver_badges_count, dummy_silver_badges_count)

    def test_bronze_badges_count(self):
        dummy_bronze_badges_count = random.randint(0, 100000)
        bronze_badges_count = StackOverflowFactory(bronze_badges_count=dummy_bronze_badges_count)
        self.assertEqual(bronze_badges_count.bronze_badges_count, dummy_bronze_badges_count)

    def test_account_creation_date(self):
        dummy_account_creation_date = fake.date_time().replace(tzinfo=pytz.utc)
        account_creation_date = StackOverflowFactory(account_creation_date=dummy_account_creation_date)
        self.assertEqual(account_creation_date.account_creation_date, dummy_account_creation_date)

    def test_last_access_date(self):
        dummy_last_access_date = fake.date_time().replace(tzinfo=pytz.utc)
        last_access_date = StackOverflowFactory(last_access_date=dummy_last_access_date)
        self.assertEqual(last_access_date.last_access_date, dummy_last_access_date)

    def test_is_moderator(self):
        dummy_is_moderator = fake.boolean()
        is_moderator = StackOverflowFactory(is_moderator=dummy_is_moderator)
        self.assertEqual(is_moderator.is_moderator, dummy_is_moderator)

    def test_total_no_of_questions(self):
        dummy_total_no_of_questions = random.randint(0, 100000)
        total_no_of_questions = StackOverflowFactory(total_no_questions=dummy_total_no_of_questions)
        self.assertEqual(total_no_of_questions.total_no_questions, dummy_total_no_of_questions)

    def test_total_no_of_answers(self):
        dummy_total_no_of_answers = random.randint(0, 100000)
        total_no_of_answers = StackOverflowFactory(total_no_answers=dummy_total_no_of_answers)
        self.assertEqual(total_no_of_answers.total_no_answers, dummy_total_no_of_answers)

    def test_reputation_change_month(self):
        dummy_reputation_change_month = random.randint(-1000, 100000)
        reputation_change_month = StackOverflowFactory(reputation_change_month=dummy_reputation_change_month)
        self.assertEqual(reputation_change_month.reputation_change_month, dummy_reputation_change_month)

    def test_reputation_change_quarter(self):
        dummy_reputation_change_quarter = random.randint(-1000, 100000)
        reputation_change_quarter = StackOverflowFactory(reputation_change_quarter=dummy_reputation_change_quarter)
        self.assertEqual(reputation_change_quarter.reputation_change_quarter, dummy_reputation_change_quarter)

    def test_reputation_change_year(self):
        dummy_reputation_change_year = random.randint(-1000, 100000)
        reputation_change_year = StackOverflowFactory(reputation_change_year=dummy_reputation_change_year)
        self.assertEqual(reputation_change_year.reputation_change_year, dummy_reputation_change_year)

    def test_reputation_score(self):
        dummy_reputation_score = random.random()
        reputation_score = StackOverflowFactory(reputation_score=dummy_reputation_score)
        self.assertEqual(reputation_score.reputation_score, dummy_reputation_score)

    def test_contribution_score(self):
        dummy_contribution_score = random.random()
        contribution_score = StackOverflowFactory(contribution_score=dummy_contribution_score)
        self.assertEqual(contribution_score.contribution_score, dummy_contribution_score)

    def test_activity_score(self):
        dummy_activity_score = random.random()
        activity_score = StackOverflowFactory(activity_score=dummy_activity_score)
        self.assertEqual(activity_score.activity_score, dummy_activity_score)


class BlogTest(TestCase):
    """Test for Blog Model"""

    def test_url(self):
        # dummy_url = 'http://yamanahlawat.org'
        url = BlogFactory(url='http://yamanahlawat.org/')
        self.assertEqual(url.url, 'http://yamanahlawat.org/')

    def test_reputation_score(self):
        dummy_reputation_score = random.random()
        reputation_score = BlogFactory(reputation_score=dummy_reputation_score)
        self.assertEqual(reputation_score.reputation_score, dummy_reputation_score)

    def test_contribution_score(self):
        dummy_contribution_score = random.random()
        contribution_score = BlogFactory(contribution_score=dummy_contribution_score)
        self.assertEqual(contribution_score.contribution_score, dummy_contribution_score)

    def test_activity_score(self):
        dummy_activity_score = random.random()
        activity_score = BlogFactory(activity_score=dummy_activity_score)
        self.assertEqual(activity_score.activity_score, dummy_activity_score)


class WebsiteTest(TestCase):
    """Test for Website Model"""

    def test_url(self):
        # dummy_url = 'http://launchyard.com'
        url = WebsiteFactory(url='http://launchyard.com/')
        self.assertEqual(url.url, 'http://launchyard.com/')

    def test_reputation_score(self):
        dummy_reputation_score = random.random()
        reputation_score = WebsiteFactory(reputation_score=dummy_reputation_score)
        self.assertEqual(reputation_score.reputation_score, dummy_reputation_score)

    def test_contribution_score(self):
        dummy_contribution_score = random.random()
        contribution_score = WebsiteFactory(contribution_score=dummy_contribution_score)
        self.assertEqual(contribution_score.contribution_score, dummy_contribution_score)

    def test_activity_score(self):
        dummy_activity_score = random.random()
        activity_score = WebsiteFactory(activity_score=dummy_activity_score)
        self.assertEqual(activity_score.activity_score, dummy_activity_score)


class MobileAppTest(TestCase):
    """
    Test for MobileApp Model
    """

    def test_reputation_score(self):
        dummy_reputation_score = random.random()
        reputation_score = MobileAppFactory(reputation_score=dummy_reputation_score)
        self.assertEqual(reputation_score.reputation_score, dummy_reputation_score)

    def test_contribution_score(self):
        dummy_contribution_score = random.random()
        contribution_score = MobileAppFactory(contribution_score=dummy_contribution_score)
        self.assertEqual(contribution_score.contribution_score, dummy_contribution_score)

    def test_activity_score(self):
        dummy_activity_score = random.random()
        activity_score = MobileAppFactory(activity_score=dummy_activity_score)
        self.assertEqual(activity_score.activity_score, dummy_activity_score)

    def test_app_url(self):
        url = MobileAppFactory(app_url='http://play.google.com/whatsapp/')
        self.assertEqual(url.app_url, 'http://play.google.com/whatsapp/')






