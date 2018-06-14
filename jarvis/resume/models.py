# -*- coding: utf-8 -*-

# django imports
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import JSONField

# App Imports
from jarvis.core.models import BaseModel

# third party imports
from autoslug import AutoSlugField
from model_utils import Choices
import uuid
from django.utils.translation import ugettext_lazy as _
from jarvis.resume.utils.ranking.skill_matching import SkillMatchingScore


class Url(BaseModel):
    """
    Model to store the urls extracted from the user's resume.
    """
    CATEGORIES = Choices(
        'contribution', 'coding', 'social',
        'blog', 'forums', 'other'
    )
    category = models.CharField(
        max_length=100, blank=True, null=True, choices=CATEGORIES,
        default=CATEGORIES.other
    )
    url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.url

    class Meta:
        ordering = ('-created_date',)


class Score(BaseModel):
    """Model for storing individual category scores."""

    TYPES = Choices(
        (0, 'coding', _('coding')),
        (1, 'social', _('social')),
        (2, 'skill_matching', _('skill matching')),
    )

    type = models.PositiveIntegerField(choices=TYPES, help_text="Type of Score")
    score = models.DecimalField(
        help_text="Individual Score Obtained", default=0.0, blank=True,
        decimal_places=2, max_digits=250
    )

    def __unicode__(self):
        return _("Score Type: %s") % self.type

    class Meta:
        ordering = ("-type", )


class Skill(BaseModel):
    """Model for storing skills entered."""

    name = models.CharField(max_length=250, blank=True, null=True, unique=True)
    slug = AutoSlugField(unique=True, populate_from='name', always_update=True)

    def __unicode(self):
        return _("Skill Name: %s") % self.name

    class Meta:
        ordering = ('-name', )


class TrialUser(BaseModel):
    """
    Model to store user information who used trial version.
    """
    email_address = models.EmailField(
        help_text="Email of user who used Trial Service"
    )

    def __unicode__(self):
        return self.email_address


class Location(BaseModel):
    """
    Model to store location names.
    """
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ('-name', )


class Company(BaseModel):
    """
    Model to store company names.
    """
    location = models.ForeignKey(Location, null=True)
    name = models.CharField(max_length=150, blank=True, null=True, unique=True)
    rank = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ('-name', )


class Institution(BaseModel):
    """
    Model to store institution names.
    """
    location = models.ForeignKey(Location, null=True)
    name = models.CharField(max_length=400, blank=True, null=True, unique=True)
    score = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ('-name', )


class Resume(BaseModel):
    """Model for storing all the resume details."""

    urls = models.ManyToManyField(Url)
    scores = models.ManyToManyField(Score)
    skills = models.ManyToManyField('Skill', through='ResumeSkills', through_fields=('resume', 'skill'))
    locations = models.ManyToManyField(Location)
    companies = models.ManyToManyField(Company)
    institutions = models.ManyToManyField(Institution)
    user = models.ForeignKey(User, null=True, related_name='resumes')
    trial_user = models.ForeignKey(
        TrialUser,
        null=True,
        related_name='trial_user',
        on_delete=models.CASCADE
    )

    STATUS = Choices(
        (0, 'processing', _('processing')),
        (1, 'processed', _('processed')),
    )

    parse_status = models.PositiveIntegerField(choices=STATUS)
    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    file_name = models.CharField(max_length=50, blank=True)
    content_hash = models.TextField(help_text=_("Hash generated from jarvis.resume and skills."), db_index=True, default='')
    content = models.TextField(help_text=_("Parsed text obtained from jarvis.resume."))
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    phone_number = models.TextField(blank=True, default='')
    # experience in years
    experience = models.FloatField(blank=True, null=True)
    resume_location = models.URLField(help_text='Path to resume', null=True)
    total_score = models.DecimalField(
        help_text="Total Score Obtained", default=0.0, blank=True,
        decimal_places=2, max_digits=250
    )

    def __unicode__(self):
        return _("ID: %s") % self.id

    class Meta:
        ordering = ("-created_date", )

    def get_skill_score(self):
        all_skills = self.skills.all()
        skills = []
        for skill in all_skills:
            skills.append(skill.name)
        string_of_skills = ', '.join(skills)
        skill_matching_instance = SkillMatchingScore(skills=string_of_skills, text=self.content)
        score = skill_matching_instance.get_score()
        return score['score']


class Visitor(BaseModel):
    user = models.ForeignKey(
        User, related_name='visit_history',
        null=True, on_delete=models.CASCADE,
    )
    ip_address = models.CharField(max_length=40, blank=True)
    query_string = JSONField()
    last_active = models.DateTimeField()
    referer = models.TextField(blank=True)
    user_agent = models.CharField(max_length=250, blank=True)
    pageview = models.CharField(max_length=40, blank=True)
    method = models.CharField(max_length=10, blank=True)


class ResumeSkills(BaseModel):
    """Model for storing through relationship between Resume and Skills"""

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    is_matched = models.BooleanField(default=False)

    def __unicode__(self):
        return _("Skill Matched: %s") % self.is_matched

    class Meta:
        ordering = ('-created_date', )
        unique_together = ('resume', 'skill', )


class Tag(BaseModel):
    """Model for storing all the tag names"""
    tag = models.CharField(max_length=100, help_text="Tag/Language Names")
    slug = AutoSlugField(unique=True, populate_from='tag', always_update=True)

    def __unicode__(self):
        return "%s" % self.tag

    class Meta:
        ordering = ('tag', )


class GitHubRepo(BaseModel):
    """
    Model to store github's repository details.
    """
    repo_id = models.IntegerField(unique=True)
    repo_name = models.CharField(max_length=50)
    repo_url = models.URLField(help_text="Repository's github url")
    repo_owner = models.CharField(max_length=50, help_text='Username of the user who owns the repo')
    is_forked = models.BooleanField(default=False)
    repo_organization = models.CharField(max_length=50, blank=True, help_text="Name of organisation", null=True)
    repo_language = models.ManyToManyField(Tag)
    no_of_forks = models.IntegerField()
    no_of_stars = models.IntegerField()
    no_of_watchers = models.IntegerField()
    open_issue_counts = models.IntegerField()
    repo_created_at = models.DateTimeField(help_text="Date and time when the repo was created")
    repo_updated_at = models.DateTimeField(help_text="Date and time when the repo was last updated.")
    last_pushed_at = models.DateTimeField(help_text="Date and time when last push was made.")
    repo_size = models.PositiveIntegerField(help_text="Repo size in bytes", blank=True)

    def __unicode__(self):
        return "%s" % self.repo_name

    class Meta:
        ordering = ('-created_date', )


class GitHub(BaseModel):
    """
    Model to store the github user details
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    user_id = models.IntegerField(help_text="User's Github id")
    user_name = models.CharField(max_length=50, help_text="User's Github Username")
    profile_name = models.CharField(max_length=50, blank=True, help_text="User's Full Name", null=True)
    email = models.EmailField(help_text="User's Email", null=True)
    profile_url = models.URLField(help_text="User's Github Url")
    profile_image_url = models.URLField(help_text="User's profile image url")
    gists_url = models.URLField(help_text="Github's API url for all user gists")
    location = models.CharField(max_length=100, blank=True, help_text="User's Location", null=True)
    blog_url = models.URLField(help_text="User's Website/Blog Url", blank=True, null=True)
    company = models.CharField(max_length=50, help_text="Company the user is currently working in.", null=True)
    followers = models.PositiveIntegerField()
    following = models.PositiveIntegerField()
    hireable = models.NullBooleanField(null=True)
    public_repos = models.PositiveIntegerField(help_text="Number of Public repository")
    total_private_repos = models.PositiveIntegerField(help_text="Total Number of Private repository", null=True)
    owned_private_repos = models.PositiveIntegerField(help_text="Private repositories owned by User", null=True)
    public_gists = models.PositiveIntegerField(help_text="Public gists owned by User", null=True)
    private_gists = models.PositiveIntegerField(help_text="Private gists owned by User", null=True)
    account_created_at = models.DateField(help_text="Date of User's Account Creation")
    repo_updated_at = models.DateTimeField(help_text="Date when user updated a repository")
    account_modified_at = models.DateTimeField(help_text="Date when user modified the account")
    reputation_score = models.FloatField(default=0)
    contribution_score = models.FloatField(default=0)
    activity_score = models.FloatField(default=0)

    def __unicode__(self):
        return "%s" % self.user_name

    class Meta:
        ordering = ('-created_date', )


class BitBucket(BaseModel):
    """ Model for storing Bit Bucket User Details"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=50, help_text="User's BitBucket Username")
    display_name = models.CharField(max_length=50, help_text="User's full name")
    account_created_at = models.DateTimeField(help_text="Date of user's account creation")
    total_no_public_repos = models.PositiveIntegerField()
    following = models.PositiveIntegerField()
    followers = models.PositiveIntegerField()
    blog_url = models.URLField(help_text="uses's website/blog url", blank=True, null=True)
    profile_url = models.URLField(help_text="User's BitBucket Url")
    repositories_url = models.URLField(help_text="Url to list all the user's repositories", blank=True)
    snippet_url = models.URLField(help_text="User's bit bucket snippet url")
    location = models.CharField(max_length=100, blank=True, help_text="User's Location")
    reputation_score = models.FloatField(default=0)
    contribution_score = models.FloatField(default=0)
    activity_score = models.FloatField(default=0)

    def __unicode__(self):
        return "%s" % self.user_name

    class Meta:
        ordering = ('-created_date', )


class StackOverflow(BaseModel):
    """
    Model to store StackOverFlow User details.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    user_id = models.PositiveIntegerField(help_text="User's StackOverflow id")
    profile_name = models.CharField(max_length=50, blank=True, help_text="User's Display Name on StackOverflow")
    location = models.CharField(max_length=100, blank=True, help_text="User's Location")
    website_url = models.URLField(help_text="User's Website/Blog Url", blank=True, null=True)
    profile_url = models.URLField(help_text="User's StackOverFlow Url")
    profile_image_url = models.URLField(help_text="User's profile image Url.")
    reputation = models.IntegerField()
    gold_badges_count = models.PositiveIntegerField()
    silver_badges_count = models.PositiveIntegerField()
    bronze_badges_count = models.PositiveIntegerField()
    top_answer_tags = models.ManyToManyField(Tag, related_name="stackoverflowusers_answers")
    top_question_tags = models.ManyToManyField(Tag, related_name="stackoverflowusers_questions")
    account_creation_date = models.DateTimeField(help_text="Date when the Account was created")
    last_access_date = models.DateTimeField(help_text="Date when the account was last accessed")
    is_moderator = models.BooleanField(help_text="checks if the user is moderator")
    total_no_questions = models.PositiveIntegerField()
    total_no_answers = models.PositiveIntegerField()
    reputation_change_month = models.IntegerField(help_text="Reputation change this month", blank=True, null=True)
    reputation_change_quarter = models.IntegerField(help_text="Reputation change this quarter", blank=True, null=True)
    reputation_change_year = models.IntegerField(help_text="Reputation change this year", blank=True, null=True)
    reputation_score = models.FloatField(default=0)
    contribution_score = models.FloatField(default=0)
    activity_score = models.FloatField(default=0)

    def __unicode__(self):
        return "%s" % self.user_id

    class Meta:
        ordering = ('-created_date', )


class MobileApp(BaseModel):
    """
    Model to store Play Store App details.
    """
    TYPES = Choices(
        ("android", "Android"), ("ios", "iOS"),
    )
    app_type = models.CharField(max_length=20, choices=TYPES)
    app_url = models.CharField(
        max_length=500, blank=True, help_text="Application Website"
    )

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)

    rating_ios = models.PositiveIntegerField(null=True, blank=True, default=None)
    customer_rating_for_all_version_ios = models.FloatField(null=True, blank=True, default=None)
    customer_rating_for_current_version_ios = models.FloatField(null=True, blank=True, default=None)
    total_customer_rating = models.FloatField(null=True, blank=True, default=None)
    last_updated_date = models.DateField(blank=True, null=True)

    ratings_android = models.FloatField(null=True, blank=True, default=None)
    installs_android = models.FloatField(null=True, blank=True, default=None)

    reputation_score = models.FloatField(default=0)
    contribution_score = models.FloatField(default=0)
    activity_score = models.FloatField(default=0)

    def __unicode__(self):
        return "%s" % self.app_url

    class Meta:
        ordering = ('-created_date', )


class Blog(BaseModel):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    reputation_score = models.FloatField()
    contribution_score = models.FloatField()
    activity_score = models.FloatField()
    url = models.URLField()

    def __unicode__(self):
        return "%s" % self.url

    class Meta:
        ordering = ('-created_date', )


class Website(BaseModel):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    reputation_score = models.FloatField()
    contribution_score = models.FloatField()
    activity_score = models.FloatField()
    url = models.URLField()

    def __unicode__(self):
        return "%s" % self.url

    class Meta:
        ordering = ('-created_date', )
