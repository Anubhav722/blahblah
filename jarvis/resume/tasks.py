# Standard Library
import json
try:
    from urllib.error import HTTPError
except:
    from urllib2 import HTTPError

# Third Party
import requests
from celery import task

# App Imports
from jarvis.resume.skillset import skillset
from jarvis.resume.models import (
    Skill, Url, Resume, Score, Location, Company, Institution, ResumeSkills
)
from jarvis.resume.utils.machine_learning.helper import FeatureExtraction
from jarvis.resume.utils.machine_learning.features import ExtractFeatures
from jarvis.resume.utils.parser_helper import (
    get_urls, url_categories, get_url_response, get_stackoverflow_userid,
    get_github_username, get_bitbucket_username, get_bit_bucket_url
)
from jarvis.resume.helpers import (
    get_basics, get_skill_matching_score, apply_stackoverflow_score,
    apply_github_score, apply_play_store_app_score, apply_itunes_score,
    apply_blog_score, apply_website_score, apply_bitbucket_score,
    save_resume_skills, calculate_blog_scores, calculate_website_scores,
    calculate_average_mobile_contrib_score, check_file_name_length,
    callback_internal_client
)


@task
def parse_resume(
    path, text, resume_id, skills, file_name, hash_value, callback_client=False):
    content_list = text.lower().split()

    # Get resume instance.
    resume_details = Resume.objects.get(id=resume_id)
    # Categorising urls
    categories_url = url_categories(get_urls(text))
    # Getting custom url response using get_url_response
    url_response = get_url_response(categories_url)

    # Get basic details.
    first_name, last_name, phone_number, email = get_basics(path)

    # Consider basic details only if resume_details for the same is non-nil.
    if resume_details.email:
        email = resume_details.email
    if resume_details.first_name:
        first_name = resume_details.first_name
    if resume_details.last_name:
        last_name = resume_details.last_name
    if resume_details.phone_number:
        phone_number = resume_details.phone_number

    # Url Instance
    for item in url_response:
        resume_urls = Url.objects.filter(url=item['name'])
        if resume_urls.exists():
            resume_url = resume_urls[0]
            resume_url.category = item['type']
            resume_url.save()
        else:
            resume_url = Url.objects.create(
                url=item['name'], category=item['type']
            )

        resume_details.urls.add(resume_url)

    # Skills Matching Score
    (skill_match_score,
    skills_matched,
    skills_not_matched) = get_skill_matching_score(skills, text)

    # Definition of scores
    github_contribution_score = 0
    github_activity_score = 0
    github_reputation_score = 0
    bit_bucket_contribution_score = 0
    bit_bucket_activity_score = 0
    bit_bucket_reputation_score = 0
    stackoverflow_contribution_score = 0
    stackoverflow_reputation_score = 0
    stackoverflow_activity_score = 0

    # StackOverflow Score
    stackoverflow_user_id = get_stackoverflow_userid(text)
    if stackoverflow_user_id:
        (stackoverflow_activity_score,
        stackoverflow_reputation_score,
        stackoverflow_contribution_score) = apply_stackoverflow_score(
            stackoverflow_user_id, resume_details
        )

    # GitHub Score
    github_username = get_github_username(text)
    if github_username:
        (github_activity_score,
        github_reputation_score,
        github_contribution_score) = apply_github_score(
            github_username, resume_details
        )

    # Blog score
    apply_blog_score(categories_url, resume_details)

    # BitBucket Score
    contribution_urls = categories_url['contributions']
    bit_bucket_url = get_bit_bucket_url(contribution_urls)
    if bit_bucket_url == 'No Url Found' or bit_bucket_url is None:
        pass
    else:
        bit_bucket_user_name = get_bitbucket_username(bit_bucket_url)
        (bit_bucket_activity_score,
        bit_bucket_reputation_score,
        bit_bucket_contribution_score) = apply_bitbucket_score(
            bit_bucket_user_name, resume_details
        )

    # MobileApp Database saving and score calculations
    # Play Store - Total Score
    apply_play_store_app_score(categories_url, resume_details)
    # ITunes - Total Score
    apply_itunes_score(categories_url, first_name, resume_details)

    # Website Score
    (website_activity_score,
    website_reputation_score,
    website_contribution_score) = apply_website_score(
        categories_url, resume_details, email
    )

    save_resume_skills(resume_details, skills_matched, skills_not_matched)

    # Work Experience
    features = FeatureExtraction()
    work_experience = features.get_work_experience(text)

    # Blog
    (average_blog_activity_score,
    average_blog_reputation_score,
    average_blog_contribution_score) = calculate_blog_scores(resume_details)

    # Website
    (average_website_activity_score,
    average_website_reputation_score,
    average_website_contribution_score) = calculate_website_scores(resume_details)

    # average mobile contribution score
    (average_mobile_app_activity_score,
    average_mobile_app_reputation_score,
    average_mobile_app_contribution_score) = calculate_average_mobile_contrib_score(resume_details)

    # Activity Scores
    blog_activity_score = average_blog_activity_score
    website_activity_score = average_website_activity_score
    mobile_app_activity_score = average_mobile_app_activity_score

    # Contributions Scores
    blog_contribution_score = average_blog_contribution_score
    website_contribution_score = average_website_contribution_score
    mobile_app_contribution_score = average_mobile_app_contribution_score

    # Reputation Scores
    blog_reputation_score = average_blog_reputation_score
    website_reputation_score = average_website_reputation_score
    mobile_app_reputation_score = average_mobile_app_reputation_score

    # Total Contribution Score
    coding_total_contribution_score = (
        github_contribution_score +
        bit_bucket_contribution_score +
        stackoverflow_contribution_score +
        mobile_app_contribution_score
    )
    social_total_contribution_score = (
        blog_contribution_score + website_contribution_score
    )

    # Total Activity score
    coding_total_activity_score = (
        github_activity_score +
        stackoverflow_activity_score +
        bit_bucket_activity_score +
        mobile_app_activity_score
    )
    social_total_activity_score = blog_activity_score + website_activity_score

    # Total Reputation Score
    coding_total_reputation_score = (
        github_reputation_score +
        stackoverflow_reputation_score +
        bit_bucket_reputation_score +
        mobile_app_reputation_score
    )
    social_total_reputation_score = (
        blog_reputation_score + website_reputation_score
    )

    # Total Coding score 2.5 out of 5
    total_coding_score = (
        coding_total_contribution_score +
        coding_total_reputation_score +
        coding_total_activity_score
    )
    # Total Social Score 1.5 out 5
    total_social_score = (
        social_total_contribution_score +
        social_total_activity_score +
        social_total_reputation_score
    )
    # Total Skill Matching Score 1 out 5
    total_skill_score = skill_match_score

    # Saving to Scores Model
    # saving total contribution score
    coding_score_instance = Score.objects.create(
        type=Score.TYPES.coding,
        score=total_coding_score
    )
    resume_details.scores.add(coding_score_instance)

    social_score_instance = Score.objects.create(
        type=Score.TYPES.social,
        score=total_social_score
    )
    resume_details.scores.add(social_score_instance)

    skill_score_instance = Score.objects.create(
        type=Score.TYPES.skill_matching,
        score=total_skill_score
    )
    resume_details.scores.add(skill_score_instance)

    total_ranking = total_coding_score + total_social_score + total_skill_score

    # Extracting Location, Company and Institution Names
    extract_features = ExtractFeatures()
    locations = extract_features.get_location(text)
    companies = extract_features.get_company_names(text)
    institutions = extract_features.get_institution_names(text)
    for location in locations:
        location_instance, created = Location.objects.get_or_create(name=location)
        resume_details.locations.add(location_instance)
    for company in companies:
        company_instance, created = Company.objects.get_or_create(name=company)
        resume_details.companies.add(company_instance)
    for institution in institutions:
        institution_instance, created = Institution.objects.get_or_create(name=institution)
        resume_details.institutions.add(institution_instance)

    # Extract skills from provided text.
    # NOTE: As per now we're getting top 1000 tags from SO to extract skills.
    # With those skills we're getting intersection with list of content text.
    # Need to find better solution to do so [Bloom filter, et cetera]
    
    import re
    content_list = map(lambda x: re.sub('[^0-9a-zA-Z\.]+', '', x), content_list)
    # print(content_list)
    # content_list = map(lambda x: x.replace(',', ''), content_list)
    matched_skills = list(skillset.intersection(content_list))
    for skill in matched_skills:
         skill_instance, created = Skill.objects.get_or_create(name=skill)
         rskills = ResumeSkills(resume=resume_details, skill=skill_instance)
         rskills.save()

    # Resume
    file_name = check_file_name_length(file_name)
    resume_details.first_name = first_name
    resume_details.last_name = last_name
    resume_details.phone_number = phone_number
    resume_details.parse_status = Resume.STATUS.processed
    resume_details.file_name = file_name
    resume_details.content_hash = hash_value
    resume_details.content = text
    resume_details.email = email
    resume_details.resume_location = path
    resume_details.experience = work_experience
    resume_details.total_score = total_ranking
    resume_details.save()

    if callback_client:
        resp = callback_internal_client(resume_details)
        if resp.status_code != requests.codes.ok:
            print(
                "ERROR: Unable to callback to internal client for resume: %s".format(
                str(resume_id)
            ))

    return "Resume Processed"
