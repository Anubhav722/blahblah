from ..models import (Url, Resume, Skill, ResumeSkills, Score, BitBucket, Tag,
                      GitHub, StackOverflow, MobileApp, Website, Blog)
from factory import django, fuzzy, SubFactory
from faker import Faker
import random
import pytz


fake = Faker()

URL_CATEGORIES = [x[0] for x in Url.CATEGORIES]
SCORE_TYPES = [x[0] for x in Score.TYPES]
RESUME_STATUS = [x[0] for x in Resume.STATUS]
APP_TYPE = [x[0] for x in MobileApp.TYPES]


class UrlFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for Testing URL Model
    """
    class Meta:
        model = Url

    url = fake.url()
    category = fuzzy.FuzzyChoice(URL_CATEGORIES)


class ScoreFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing Score Model
    """
    class Meta:
        model = Score

    type = fuzzy.FuzzyChoice(SCORE_TYPES)


class SkillFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing Skill Model
    """
    class Meta:
        model = Skill

    name = fake.first_name()
    slug = fake.slug()


class ResumeFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing Resume Model
    """
    class Meta:
        model = Resume
        django_get_or_create = ('id', )

    id = fake.uuid4()
    file_name = fake.name() + '.pdf'
    content_hash = fake.text()
    content = fake.text()
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    phone_number = str(fake.random_number(10))
    parse_status = fuzzy.FuzzyChoice(RESUME_STATUS)


class ResumeSkillsFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing ResumeSkills Model
    """
    class Meta:
        model = ResumeSkills

    is_matched = fake.boolean()
    resume = SubFactory(ResumeFactory)
    skill = SubFactory(SkillFactory)


class BitBucketFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing BitBucket Model
    """
    class Meta:
        model = BitBucket

    user_name = fake.first_name().lower()
    display_name = fake.name()
    account_created_at = fake.date_time().replace(tzinfo=pytz.utc)
    total_no_public_repos = random.randint(0, 99)
    following = fake.random_number()
    followers = fake.random_number()
    blog_url = fake.url()
    profile_url = fake.url()
    repositories_url = fake.url()
    snippet_url = fake.url()
    location = fake.state()
    reputation_score = random.random()
    contribution_score = random.random()
    activity_score = random.random()
    resume = SubFactory(ResumeFactory)


class TagFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing Tag Model
    """
    class Meta:
        model = Tag

    tag = fake.first_name().lower()
    slug = fake.slug()


class GitHubFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing GitHub Model
    """
    class Meta:
        model = GitHub

    user_id = random.randint(1, 100000)
    user_name = fake.first_name().lower()
    profile_name = fake.name()
    email = fake.email()
    profile_url = fake.url()
    profile_image_url = fake.url()
    gists_url = fake.url()
    location = fake.state()
    blog_url = fake.url()
    company = fake.company()
    followers = random.randint(0, 100000)
    following = random.randint(0, 100000)
    hireable = fake.boolean()
    public_repos = random.randint(0, 500)
    total_private_repos = random.randint(0, 500)
    owned_private_repos = random.randint(0, 500)
    public_gists = random.randint(0, 500)
    private_gists = random.randint(0, 500)
    account_created_at = fake.date_time().replace(tzinfo=pytz.utc)
    repo_updated_at = fake.date_time().replace(tzinfo=pytz.utc)
    account_modified_at = fake.date_time().replace(tzinfo=pytz.utc)
    reputation_score = random.random()
    contribution_score = random.random()
    activity_score = random.random()
    resume = SubFactory(ResumeFactory)


class StackOverflowFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing StackOverflow Model
    """
    class Meta:
        model = StackOverflow

    user_id = random.randint(1, 1000000)
    profile_name = fake.name()
    location = fake.state()
    website_url = fake.url()
    profile_url = fake.url()
    profile_image_url = fake.url()
    reputation = random.randint(0, 100000)
    gold_badges_count = random.randint(0, 100000)
    silver_badges_count = random.randint(0, 100000)
    bronze_badges_count = random.randint(0, 100000)
    account_creation_date = fake.date_time().replace(tzinfo=pytz.utc)
    last_access_date = fake.date_time().replace(tzinfo=pytz.utc)
    is_moderator = fake.boolean()
    total_no_questions = random.randint(0, 100000)
    total_no_answers = random.randint(0, 100000)
    reputation_change_month = random.randint(-1000, 100000)
    reputation_change_quarter = random.randint(-1000, 100000)
    reputation_change_year = random.randint(-1000, 100000)
    reputation_score = random.random()
    contribution_score = random.random()
    activity_score = random.random()
    resume = SubFactory(ResumeFactory)


class MobileAppFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing MobileApp model.
    """
    class Meta:
        model = MobileApp

    app_type = fuzzy.FuzzyChoice(APP_TYPE)
    app_url = fake.url()
    reputation_score = random.random()
    contribution_score = random.random()
    activity_score = random.random()
    resume = SubFactory(ResumeFactory)


class BlogFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing Blog model.
    """
    class Meta:
        model = Blog

    reputation_score = random.random()
    contribution_score = random.random()
    activity_score = random.random()
    url = fake.url()
    resume = SubFactory(ResumeFactory)


class WebsiteFactory(django.DjangoModelFactory):
    """
    Fake Model Factory for testing Website Model.
    """
    class Meta:
        model = Website

    reputation_score = random.random()
    contribution_score = random.random()
    activity_score = random.random()
    url = fake.url()
    resume = SubFactory(ResumeFactory)

