# Standard library
import sys
import string
import logging
import difflib
import datetime
from os.path import splitext
from urllib2 import HTTPError

# Third party
import boto
import requests
from uuid import uuid4
from gensim import models
from boto.s3.key import Key


# Django
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# DRF
from rest_framework.response import Response

# App
from .models import Resume, Url
from jarvis.resume.utils.ranking.blog import get_url_details, BlogScore
from jarvis.resume.utils.resume_parser import extract_resume, trim_non_alpha
from jarvis.resume.utils.ranking.github import GitHubScore
from jarvis.resume.utils.ranking.itunes import ItunesScore
from jarvis.resume.utils.ranking.website import WebsiteScore
from jarvis.resume.utils.ranking.bit_bucket import BitBucketScore
from jarvis.resume.utils.ranking.stackoverflow import StackOverflowScore
from jarvis.resume.utils.ranking.skill_matching import SkillMatchingScore
from jarvis.resume.utils.ranking.play_store_app import PlayStoreAppRating
from jarvis.resume.api.serializers import (
    ResumeParseInternalSerializer, ResumeCallbackSerializer
)
from jarvis.resume.utils.resume_parser import extract_resume
from jarvis.resume.utils.parser_helper import (
    get_urls, url_categories, get_url_response
)
from .constants import (
    SKILL_MAPPER, SHORT_SKILL_MAPPER, GOOD_HIRE, BAD_HIRE
)
from .models import (
    Tag, Blog, Website, GitHub, MobileApp, BitBucket, StackOverflow,
    Skill, ResumeSkills, Resume,
)
from jarvis.settings.staging import (
    AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_STORAGE_BUCKET_NAME,
    AWS_S3_CUSTOM_DOMAIN
)

# Global vars
logger = logging.getLogger(__file__)
MAX_FILE_NAME_LENGTH = Resume._meta.get_field('file_name').max_length

# ------------------------------------------------------------------------------

def hireable(score):
    if score < BAD_HIRE.higher:
        return "bad-hire"
    elif score >= GOOD_HIRE.lower:
        return "good-hire"

def criteria_to_score(criteria):
    if criteria == "good-hire":
        return GOOD_HIRE
    return BAD_HIRE

def support_short_skill_names(skill_name):
    result = list()
    skill_name = difflib.get_close_matches(
        skill_name, list(SHORT_SKILL_MAPPER.keys()), cutoff=0.6
    )
    if skill_name:
        in_short_skill_mapper = SHORT_SKILL_MAPPER.get(skill_name[0], None)
        if in_short_skill_mapper:
            skill = SKILL_MAPPER.get(in_short_skill_mapper.lower(), None)
            for k, v in SKILL_MAPPER.items():
                if v == skill:
                    result.append(k)
    return result

def get_related_technology_stack(skill_name):
    result = list()
    skill_name = difflib.get_close_matches(
        skill_name, list(SKILL_MAPPER.keys()), cutoff=0.7
    )
    if skill_name:
        skill = SKILL_MAPPER.get(skill_name[0], None)
        for k, v in SKILL_MAPPER.items():
            if v == skill:
                result.append(k)
    return result

def parse_resume_internal(path, text, resume_id, file_name, hash_value, post_data):
    urls = get_urls(text)
    categories_url = url_categories(urls)
    url_response = get_url_response(categories_url)
    resume_details = Resume.objects.get(id=resume_id)
    response = extract_resume(path)
    basics = response.get('basics')
    if basics:
        first_name = basics.get('first_name')
        last_name = basics.get('last_name')
        phone_number = basics.get('phone')
        email = basics.get('email')
        if email:
            email = email[0]

    for item in url_response:
        resume_url = Url.objects.create(category=item['type'], url=item['name'])
        resume_details.urls.add(resume_url)

    # Resume
    resume_details.first_name = post_data.get('first_name')
    resume_details.last_name = post_data.get('last_name')
    resume_details.phone_number = post_data.get('contact_no')
    resume_details.email = post_data.get('email')

    if not resume_details.first_name:
        resume_details.first_name = first_name[:45]
    if not resume_details.last_name:
        resume_details.last_name = last_name[:45]
    if not resume_details.phone_number:
        resume_details.phone_number = phone_number
    if not resume_details.email:
        resume_details.email = email

    resume_details.content = text
    resume_details.file_name = file_name
    resume_details.resume_location = path
    resume_details.content_hash = hash_value
    resume_details.parse_status = Resume.STATUS.processed
    resume_details.save()
    return resume_details

def create_resume_instance(path, text, file_name, hash_value, user, post_data):
    provided_id = post_data.get('resume_id', None)
    instance = create_resume_instance_with_provided_id(
        provided_id, user
    )

    instance = parse_resume_internal(
        path, text, instance.id, file_name, hash_value, post_data
    )

    from . import tasks
    tasks.parse_resume.delay(
        path, text, instance.id, '', file_name, hash_value,
        callback_client=True
    )
    serializer = ResumeParseInternalSerializer(instance)
    return (serializer.data)

# ------------------------------------------------------------------------------

def get_basics(path):
    res = extract_resume(path)
    basics = res.get('basics')
    if basics:
        first_name = trim_non_alpha(basics['first_name'])
        last_name = trim_non_alpha(basics['last_name'])
        phone_number = basics['phone']
        email = basics.get('email')
        if email:
            email = trim_non_alpha(basics.get('email')[0])
        else:
            email = ""
    return (
        first_name, last_name, phone_number, email
    )

# ------------------------------------------------------------------------------

def get_skill_matching_score(skills, text):
    skill_match = SkillMatchingScore(skills=skills, text=text)
    skill_details = skill_match.get_score()
    skill_match_score = skill_details['score']
    skills_matched = (','.join(map(str, skill_details['skill_matched']))).strip()
    skills_not_matched = (
        ','.join(map(str, skill_details['skill_not_matched']))
    ).strip()

    return (
        skill_match_score, skills_matched, skills_not_matched
    )

# ------------------------------------------------------------------------------

def apply_stackoverflow_score(stackoverflow_user_id, resume_details):
    stackoverflow = StackOverflowScore(stackoverflow_user_id)
    stackoverflow_reputation_score = stackoverflow.get_reputation_score()
    stackoverflow_contribution_score = stackoverflow.get_contribution_score()
    stackoverflow_activity_score = stackoverflow.get_activity_score()
    stackoverflow_total_score = stackoverflow.get_total_score()
    stackoverflow_instance = StackOverflow()
    stackoverflow_user_details = stackoverflow.get_stackoverflow_user_details()
    stackoverflow_instance.user_id = stackoverflow_user_details['user_id']
    stackoverflow_instance.profile_name = stackoverflow_user_details['profile_name']
    stackoverflow_instance.location = stackoverflow_user_details['location']
    try:
        stackoverflow_instance.website_url = stackoverflow_user_details['website_url']
    except KeyError:
        stackoverflow_instance.website_url = ''
    stackoverflow_instance.profile_url = stackoverflow_user_details['profile_url']
    stackoverflow_instance.profile_image_url = stackoverflow_user_details['profile_image_url']
    stackoverflow_instance.reputation = stackoverflow_user_details['reputation']
    stackoverflow_instance.gold_badges_count = stackoverflow_user_details['gold_badges_count']
    stackoverflow_instance.silver_badges_count = stackoverflow_user_details['silver_badges_count']
    stackoverflow_instance.bronze_badges_count = stackoverflow_user_details['bronze_badges_count']
    stackoverflow_instance.account_creation_date = stackoverflow_user_details['account_creation_date']
    stackoverflow_instance.last_access_date = stackoverflow_user_details['last_access_date']
    stackoverflow_instance.is_moderator = stackoverflow_user_details['is_moderator']
    stackoverflow_instance.total_no_questions = stackoverflow_user_details['total_no_questions']
    stackoverflow_instance.total_no_answers = stackoverflow_user_details['total_no_answers']
    stackoverflow_instance.reputation_change_month = stackoverflow_user_details['reputation_change_month']
    stackoverflow_instance.reputation_change_quarter = stackoverflow_user_details['reputation_change_quarter']
    stackoverflow_instance.reputation_change_year = stackoverflow_user_details['reputation_change_year']
    stackoverflow_instance.activity_score = stackoverflow_activity_score
    stackoverflow_instance.reputation_score = stackoverflow_reputation_score
    stackoverflow_instance.contribution_score = stackoverflow_contribution_score
    stackoverflow_instance.resume = resume_details
    stackoverflow_instance.save()

    # Tags
    top_answer_tags = stackoverflow_user_details['top_answer_tags']
    top_question_tags = stackoverflow_user_details['top_question_tags']
    for answer_tag in top_answer_tags:
        tag_answer_instance = Tag.objects.create(tag=answer_tag)
        stackoverflow_instance.top_answer_tags.add(tag_answer_instance)
    for question_tag in top_question_tags:
        tag_question_instance = Tag.objects.create(tag=question_tag)
        stackoverflow_instance.top_question_tags.add(tag_question_instance)
    stackoverflow_instance.save()

    return (
        stackoverflow_activity_score,
        stackoverflow_reputation_score,
        stackoverflow_contribution_score
    )

# ------------------------------------------------------------------------------

def apply_github_score(github_username, resume_details):
    github = GitHubScore(github_username)
    github_reputation_score = github.get_reputation_score()
    github_contribution_score = github.get_contribution_score()
    github_activity_score = github.get_activity_score()
    github_total_score = github.get_total_score(
        github_reputation_score,
        github_contribution_score,
        github_activity_score)

    # GitHub
    github_instance = GitHub()
    github_user_details = github.get_github_user_details()
    github_instance.resume = resume_details
    github_instance.user_id = github_user_details['user_id']
    github_instance.user_name = github_user_details['user_name']
    github_instance.profile_name = github_user_details['profile_name']
    github_instance.email = github_user_details['email']
    github_instance.profile_url = github_user_details['profile_url']
    github_instance.profile_image_url = github_user_details['profile_image_url']
    github_instance.gists_url = github_user_details['gists_url']
    github_instance.location = github_user_details['location']
    github_instance.blog_url = github_user_details['blog_url']
    github_instance.company = github_user_details['company']
    github_instance.followers = github_user_details['followers']
    github_instance.following = github_user_details['following']
    github_instance.hireable = github_user_details['hireable']
    github_instance.public_repos = github_user_details['public_repos']
    github_instance.total_private_repos = github_user_details['total_private_repos']
    github_instance.owned_private_repos = github_user_details['owned_private_repos']
    github_instance.public_gists = github_user_details['public_gists']
    github_instance.private_gists = github_user_details['private_gists']
    github_instance.account_created_at = github_user_details['account_created_at']
    github_instance.repo_updated_at = github_user_details['last_updated_at']
    github_instance.account_modified_at = github_user_details['last_modified']
    github_instance.activity_score = github_activity_score
    github_instance.reputation_score = github_reputation_score
    github_instance.contribution_score = github_contribution_score
    github_instance.save()

    return (
        github_activity_score,
        github_reputation_score,
        github_contribution_score
    )

# ------------------------------------------------------------------------------

def apply_bitbucket_score(bit_bucket_user_name, resume_details):
    bit_bucket = BitBucketScore(bit_bucket_user_name)
    bit_bucket_reputation_score = bit_bucket.get_reputation_score()
    bit_bucket_activity_score = bit_bucket.get_activity_score()
    bit_bucket_contribution_score = bit_bucket.get_contribution_score()
    bit_bucket_total_score = bit_bucket.get_total_score(
        bit_bucket_activity_score,
        bit_bucket_contribution_score,
        bit_bucket_reputation_score)

    # Bitbucket
    bitbucket_instance = BitBucket()
    bit_bucket_user_details = bit_bucket.get_bit_bucket_user_details()
    bitbucket_instance.resume = resume_details
    bitbucket_instance.user_name = bit_bucket_user_details['user_name']
    bitbucket_instance.display_name = bit_bucket_user_details['display_name']
    bitbucket_instance.account_created_at = bit_bucket_user_details['account_created_at']
    bitbucket_instance.total_no_public_repos = bit_bucket_user_details['total_no_of_repos']
    bitbucket_instance.following = bit_bucket_user_details['following']
    bitbucket_instance.followers = bit_bucket_user_details['followers']
    if bit_bucket_user_details['followers']:
        bitbucket_instance.blog_url = bit_bucket_user_details['blog_url']
    else:
        bitbucket_instance.blog_url = ''
    bitbucket_instance.profile_url = bit_bucket_user_details['profile_url']
    bitbucket_instance.repositories_url = bit_bucket_user_details['repo_url']
    bitbucket_instance.snippet_url = bit_bucket_user_details['snippets_url']
    if bit_bucket_user_details['location']:
        bitbucket_instance.location = bit_bucket_user_details['location']
    else:
        bitbucket_instance.location = ''
    bitbucket_instance.reputation_score = bit_bucket_reputation_score
    bitbucket_instance.contribution_score = bit_bucket_contribution_score
    bitbucket_instance.activity_score = bit_bucket_activity_score
    bitbucket_instance.save()

    return (
        bit_bucket_activity_score,
        bit_bucket_reputation_score,
        bit_bucket_contribution_score
    )

# ------------------------------------------------------------------------------

def apply_itunes_score(categories_url, first_name, resume_details):
    itunes_app_urls = [instance for instance in categories_url['apps'] if 'itunes.apple.com' in instance]
    if itunes_app_urls:
        for url in itunes_app_urls:
            itunes_activity_score = 0
            itunes_reputation_score = 0
            itunes_contribution_score = 0
            rating_ios = None
            updated_date = None
            customer_rating_for_all_version_ios = None
            customer_rating_for_current_version_ios = None
            total_customer_rating = None

            try:
                itunes_score_instance = ItunesScore(url, first_name)
                itunes_total_score = itunes_score_instance.get_total_score()
                itunes_reputation_score = itunes_score_instance.get_reputation_score()
                itunes_contribution_score = itunes_score_instance.get_contribution_score()
                itunes_activity_score = itunes_score_instance.get_activity_score()
                rating_ios = itunes_score_instance.rating
                last_updated_date = itunes_score_instance.app_last_updated_date
                customer_rating_for_all_version_ios = itunes_score_instance.no_of_customer_rating_for_all_version
                total_customer_rating = itunes_score_instance.total_customer_rating
                if last_updated_date is not None:
                    try:
                        updated_date = datetime.datetime.strptime(last_updated_date,'%b %d, %Y').date()
                    except ValueError:
                        updated_date = datetime.datetime.strptime(last_updated_date, '%d %B %Y').date()
            except HTTPError as e:
                logger.debug('HTTPError: code: {}, msg: {}in apply_itunes_score'.format(e.code, e.msg))
                print(('HTTP Error: ', e.code, e.msg))

            MobileApp.objects.create(
                resume=resume_details,
                app_type='ios',
                app_url=url,
                reputation_score=itunes_reputation_score,
                contribution_score=itunes_contribution_score,
                activity_score=itunes_activity_score,
                rating_ios=rating_ios,
                last_updated_date=updated_date,
                customer_rating_for_all_version_ios=customer_rating_for_all_version_ios,
                customer_rating_for_current_version_ios=customer_rating_for_current_version_ios,
                total_customer_rating=total_customer_rating
            )

# ------------------------------------------------------------------------------

def apply_play_store_app_score(categories_url, resume_details):
    android_app_urls = [instance for instance in categories_url['apps'] if 'play.google.com/store/apps/details' in instance]

    if android_app_urls:
        for url in android_app_urls:
            play_store_reputation_score = 0
            play_store_contribution_score = 0
            play_store_activity_score = 0
            app_installs = None
            app_rating = None
            updated_date = None

            try:
                play_store_instance = PlayStoreAppRating(url)
                play_store_total_score = play_store_instance.get_total_score()
                play_store_reputation_score = play_store_instance.get_reputation_score()
                play_store_contribution_score = play_store_instance.get_contribution_score()
                play_store_activity_score = play_store_instance.get_activity_score()
                updated_date = play_store_instance.app_updated
                app_installs = play_store_instance.app_installs
                app_rating = play_store_instance.app_rating
            except HTTPError as e:
                logger.debug('HTTPError occured code: {}, msg: {}'.format(e.code, e.msg))
                print(('HTTP Error:', e.code, e.msg))

            MobileApp.objects.create(
                resume=resume_details,
                app_type='android',
                app_url=url,
                contribution_score=play_store_contribution_score,
                activity_score=play_store_activity_score,
                reputation_score=play_store_reputation_score,
                last_updated_date=updated_date,
                ratings_android=app_rating,
                installs_android=app_installs
            )

# ------------------------------------------------------------------------------

def apply_website_score(categories_url, resume_details, email):
    website_urls = categories_url['others']
    if len(website_urls) > 0 and email:
        website = WebsiteScore(email, website_urls)
        scrapped_email = website.get_scraped_email()
        if scrapped_email:
            if len(scrapped_email[0]) > 0:
                if email == scrapped_email[0][0]:
                    website_total_score = website.get_total_score()
                    website_reputation_score = website.get_reputation_score()
                    website_contribution_score = website.get_contribution_score()
                    website_activity_score = website.get_activity_score()

                    # Saving into Database
                    # Website
                    website_instance = Website()
                    website_instance.resume = resume_details
                    if len(website_urls) > 0:
                        website_instance.url = website_urls[0]
                    website_instance.reputation_score = website_reputation_score
                    website_instance.contribution_score = website_contribution_score
                    website_instance.activity_score = website_activity_score
                    website_instance.save()

                    return (
                        website_activity_score, website_reputation_score,
                        website_contribution_score
                    )

    return None, None, None

# ------------------------------------------------------------------------------

def save_resume_skills(resume_details, skills_matched, skills_not_matched):
    # resume skills
    resume_skills_instance = ResumeSkills()
    resume_skills_instance.resume = resume_details

    # matched skills
    matched_skills = skills_matched.lower().split(',')
    unmatched_skills = skills_not_matched.lower().split(',')

# ------------------------------------------------------------------------------

def calculate_blog_scores(resume_details):
    # Calculating Scores
    total_blog_activity_score = 0
    total_blog_reputation_score = 0
    total_blog_contribution_score = 0
    average_blog_activity_score = 0
    average_blog_contribution_score = 0
    average_blog_reputation_score = 0
    blog = resume_details.blog_set.all()

    if blog:
        for item in blog:
            total_blog_contribution_score += item.contribution_score
            total_blog_activity_score += item.activity_score
            total_blog_reputation_score += item.reputation_score
        average_blog_contribution_score = total_blog_contribution_score / len(blog)
        average_blog_reputation_score = total_blog_reputation_score / len(blog)
        average_blog_activity_score = total_blog_activity_score / len(blog)

    return (
        average_blog_activity_score,
        average_blog_reputation_score,
        average_blog_contribution_score
    )

# ------------------------------------------------------------------------------

def calculate_website_scores(resume_details):
    total_website_activity_score = 0
    total_website_reputation_score = 0
    total_website_contribution_score = 0
    average_website_reputation_score = 0
    average_website_activity_score = 0
    average_website_contribution_score = 0
    website = resume_details.website_set.all()

    if website:
        for item in website:
            total_website_contribution_score += item.contribution_score
            total_website_activity_score += item.activity_score
            total_website_reputation_score += item.reputation_score
        average_website_contribution_score = total_website_contribution_score / len(website)
        average_website_activity_score = total_website_activity_score / len(website)
        average_website_reputation_score = total_website_reputation_score / len(website)

    return (
        average_website_activity_score,
        average_website_reputation_score,
        average_website_contribution_score
    )

# ------------------------------------------------------------------------------

def calculate_average_mobile_contrib_score(resume_details):
    total_mobile_app_contribution_score = 0
    total_mobile_app_activity_score = 0
    total_mobile_app_reputation_score = 0
    average_mobile_app_activity_score = 0
    average_mobile_app_reputation_score = 0
    average_mobile_app_contribution_score = 0
    mobile_app = resume_details.mobileapp_set.all()
    if mobile_app:
        for item in mobile_app:
            total_mobile_app_contribution_score += item.contribution_score
            total_mobile_app_activity_score += item.activity_score
            total_mobile_app_reputation_score += item.reputation_score
        average_mobile_app_contribution_score = (
            total_mobile_app_contribution_score / len(mobile_app)
        )
        average_mobile_app_activity_score = total_mobile_app_activity_score / len(mobile_app)
        average_mobile_app_reputation_score = total_mobile_app_reputation_score / len(mobile_app)

    return (
        average_mobile_app_activity_score,
        average_mobile_app_reputation_score,
        average_mobile_app_contribution_score
    )

# ------------------------------------------------------------------------------

def apply_blog_score(categories_url, resume_details):
    blog_urls = categories_url['blog']
    no_of_blogs = len(blog_urls)
    individual_blog_score = 0
    details_url = ''
    if no_of_blogs > 0:
        for item in blog_urls:
            details_url = get_url_details(item)
            blog = BlogScore(details_url)
            blog_activity_score = blog.get_activity_score()
            blog_reputation_score = blog.get_reputation_score()
            blog_contribution_score = blog.get_contribution_score()
            blog_total_score = blog.get_total_score(blog_activity_score, blog_contribution_score, blog_reputation_score)

            # Blog
            blog_instance = Blog()
            blog_instance.resume = resume_details
            blog_instance.reputation_score = blog_reputation_score
            blog_instance.contribution_score = blog_contribution_score
            blog_instance.activity_score = blog_activity_score
            blog_instance.url = item
            blog_instance.save()

            if blog_total_score is None:
                individual_blog_score = 0
            else:
                individual_blog_score += blog_total_score

        average_blog_score = individual_blog_score / float(no_of_blogs)

# ------------------------------------------------------------------------------

# create_resume_instance_with_provided_id should create an instance of resume
# model with provided values of user and resume_id (if any).
def create_resume_instance_with_provided_id(resume_id, user):
    if resume_id:
        # Create resume instance with provided ID.
        return Resume.objects.create(
            id=resume_id, user=user, parse_status=Resume.STATUS.processing
        )

    return Resume.objects.create(
        user=user, parse_status=Resume.STATUS.processing
    )

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

def upload_to_s3(get_file, name, extension):
    connection = connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(AWS_STORAGE_BUCKET_NAME)
    key = Key(bucket)
    key.key = "media/resumes/%s%s" % (uuid4(), extension)
    key.set_contents_from_file(get_file, cb=percent_cb, num_cb=10)
    key.make_public()
    url = key.generate_url(0, query_auth=False, force_http=True)
    return url

def check_file_name_length(file_name):
    if len(file_name) > MAX_FILE_NAME_LENGTH:
        file_name, ext = splitext(file_name)
        file_name = file_name[:MAX_FILE_NAME_LENGTH - len(ext)] + ext
    return file_name

def callback_internal_client(resume):
    """
    Should callback internal client (as of now, AirCTO API) to update
    work experience and location for particular resume (applicant).

    Use case is that; in `ResumeParseInternal` API, we're only sending
    basic details of user in one go.

    As requirements changed (JobBoard and other platforms introduced);
    we've to store locations and work experience in applicant's info.
    """

    headers, payload = dict(), dict()
    serializer = ResumeCallbackSerializer(resume)
    headers["content-type"] = "application/json"
    payload["resume_details"] = serializer.data

    try:
        r = requests.post(
            settings.AIRCTO_BACKEND_CALLBACK_RESUME_URL,
            json=payload, headers=headers
        )
        return r
    except requests.exceptions.RequestException:
        print("Failed to callback to internal client. Exception occured.\n")
        print("Details: ", payload, "\n")
        pass
