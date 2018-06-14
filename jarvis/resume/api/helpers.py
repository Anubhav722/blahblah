import pytz
import datetime
from jarvis.resume.utils.ranking.blog import get_url_details
from jarvis.resume.utils.ranking.blog import get_alexa_ranking
from jarvis.settings.staging import (AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID,
                                     AWS_STORAGE_BUCKET_NAME)
import boto
from boto.s3.key import Key


def get_github_scores(github):
    """
    Calculates GitHub Contribution, Activity and Reputation Scores.
    :param github: GitHub Instance.
    :return: Tuple of individual scores.
    """
    github_contribution_score = 0
    github_activity_score = 0
    github_reputation_score = 0
    if github.exists():
        github = github[0]
        github_contribution_score = github.contribution_score
        github_activity_score = github.activity_score
        github_reputation_score = github.reputation_score
    return github_contribution_score, github_activity_score, github_reputation_score


def get_stackoverflow_scores(stackoverflow):
    """
    Calculates StackOverflow Contribution, Activity and Reputation Scores.
    :param stackoverflow: StackOverflow Instance.
    :return: Tuple of individual scores.
    """
    stackoverflow_contribution_score = 0
    stackoverflow_reputation_score = 0
    stackoverflow_activity_score = 0
    if stackoverflow.exists():
        stackoverflow = stackoverflow[0]
        stackoverflow_contribution_score = stackoverflow.contribution_score
        stackoverflow_reputation_score = stackoverflow.reputation_score
        stackoverflow_activity_score = stackoverflow.activity_score
    return stackoverflow_contribution_score, stackoverflow_reputation_score, stackoverflow_activity_score


def get_bitbucket_scores(bitbucket):
    """
    Calculates BitBucket Contribution, Activity and Reputation Scores.
    :param bitbucket: BitBucket Instance.
    :return: Tuple of individual scores.
    """
    bitbucket_contribution_score = 0
    bitbucket_activity_score = 0
    bitbucket_reputation_score = 0
    if bitbucket.exists():
        bitbucket = bitbucket[0]
        bitbucket_contribution_score = bitbucket.contribution_score
        bitbucket_activity_score = bitbucket.activity_score
        bitbucket_reputation_score = bitbucket.reputation_score
    return bitbucket_contribution_score, bitbucket_activity_score, bitbucket_reputation_score


def get_blog_scores(blog):
    """
    Calculates Blog Contribution, Activity and Reputation Scores.
    :param blog: Blog Instance.
    :return: Tuple of individual scores.
    """
    total_blog_activity_score = 0
    total_blog_reputation_score = 0
    total_blog_contribution_score = 0
    average_blog_activity_score = 0
    average_blog_contribution_score = 0
    average_blog_reputation_score = 0
    if blog.exists():
        for item in blog:
            total_blog_contribution_score += item.contribution_score
            total_blog_activity_score += item.activity_score
            total_blog_reputation_score += item.reputation_score
        average_blog_contribution_score = total_blog_contribution_score / \
                                          len(blog)
        average_blog_reputation_score = total_blog_reputation_score / \
                                        len(blog)
        average_blog_activity_score = total_blog_activity_score / len(blog)
    return average_blog_contribution_score, average_blog_reputation_score, average_blog_activity_score


def get_website_scores(website):
    """
    Calculates Website Contribution, Activity and Reputation Scores.
    :param website: website Instance.
    :return: Tuple of individual scores.
    """
    total_website_activity_score = 0
    total_website_reputation_score = 0
    total_website_contribution_score = 0
    average_website_reputation_score = 0
    average_website_activity_score = 0
    average_website_contribution_score = 0
    if website.exists():
        for item in website:
            total_website_contribution_score += item.contribution_score
            total_website_activity_score += item.activity_score
            total_website_reputation_score += item.reputation_score
        average_website_contribution_score = total_website_contribution_score / \
                                             len(website)
        average_website_activity_score = total_website_activity_score / \
                                         len(website)
        average_website_reputation_score = total_website_reputation_score / \
                                           len(website)
    return average_website_contribution_score, average_website_activity_score, average_website_reputation_score


def get_app_scores(mobile_app):
    """
    Calculates Mobile App(ios and android) Contribution, Activity and Reputation Scores.
    :param mobile_app: MobileApp Instance.
    :return: Tuple of individual scores.
    """
    total_mobile_app_contribution_score = 0
    total_mobile_app_activity_score = 0
    total_mobile_app_reputation_score = 0
    average_mobile_app_activity_score = 0
    average_mobile_app_reputation_score = 0
    average_mobile_app_contribution_score = 0
    if mobile_app.exists():
        for item in mobile_app:
            total_mobile_app_contribution_score += item.contribution_score
            total_mobile_app_activity_score += item.activity_score
            total_mobile_app_reputation_score += item.reputation_score
        average_mobile_app_contribution_score = total_mobile_app_contribution_score / \
                                                len(mobile_app)
        average_mobile_app_activity_score = total_mobile_app_activity_score / \
                                            len(mobile_app)
        average_mobile_app_reputation_score = total_mobile_app_reputation_score / \
                                              len(mobile_app)

    return average_mobile_app_contribution_score, average_mobile_app_activity_score, average_mobile_app_reputation_score


def get_years_and_months(years, months, days_passed):
    account_created = ''
    days = ''
    if int(years) == 0 and int(months) == 0:
        account_created = 'Today'
    elif int(years) == 0 and int(months) == 1:
        account_created = months + ' mo'
    elif int(years) == 0 and int(months) > 1:
        account_created = months + ' mos'
    elif int(years) == 1 and int(months) == 0:
        account_created = years + ' yr'
    elif int(years) == 1 and int(months) == 1:
        account_created = years + ' yr ' + months + ' mo'
    elif int(years) > 1 and int(months) == 0:
        account_created = years + ' yrs'
    elif int(years) > 1 and int(months) == 1:
        account_created = years + ' yrs ' + months + ' mo'
    elif int(years) > 1 and int(months) > 1:
        account_created = years + ' yrs ' + months + ' mos'

    if days_passed == 1:
        days = '%s day' % days_passed
    elif days_passed == 0:
        days = 'Today'
    else:
        days = '%s days' % days_passed
    return account_created, days


def get_stackoverflow_details(stackoverflow):
    """
    This function fetches the stackoverflow details.
    :param stackoverflow: Stackoverflow Instance
    :return: dict : Dictionary of stackoverflow details
    """

    today_date = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    years_passed = ((today_date - stackoverflow.account_creation_date).days / 30)/float(12)
    years, months = "{0:.1f}".format(years_passed).split('.')
    days_passed = (today_date - stackoverflow.last_access_date).days
    account_created, days = get_years_and_months(years, months, days_passed)

    details = [{'name': 'Reputation', 'count': stackoverflow.reputation},
               {'name': 'Gold Badges', 'count': stackoverflow.gold_badges_count},
               {'name': 'Silver Badges', 'count': stackoverflow.silver_badges_count},
               {'name': 'Bronze Badges', 'count': stackoverflow.bronze_badges_count},
               {'name': 'Total number of questions', 'count': stackoverflow.total_no_questions},
               {'name': 'Total number of answers', 'count': stackoverflow.total_no_answers},
               {'name': 'Account Created', 'count': account_created},
               {'name': 'Last Activity', 'count': days},
               ]
    return details


def get_github_details(github):
    today_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    today_date = today_datetime.date()
    years_passed = ((today_date - github.account_created_at).days / 30) / float(12)
    years, months = "{0:.1f}".format(years_passed).split('.')
    try:
        days_passed = (today_datetime - github.repo_updated_at).days
    except TypeError:
        days_passed = (today_date - github.repo_updated_at).days
    account_created, days = get_years_and_months(years, months, days_passed)

    details = [
        {'name': 'Followers', 'count': github.followers},
        {'name': 'Following', 'count': github.following},
        {'name': 'Repositories', 'count': github.public_repos},
        {'name': 'Gists', 'count': github.public_gists},
        {'name': 'Account Created', 'count': account_created},
        {'name': 'Last Activity', 'count': days},

    ]
    return details


def get_bitbucket_details(bitbucket):
    today_date = datetime.date.today()
    years_passed = ((today_date - bitbucket.account_created_at.date()).days / 30) / float(12)
    years, months = "{0:.1f}".format(years_passed).split('.')
    days_passed = 0
    account_created, days = get_years_and_months(years, months, days_passed)

    details = [
        {'name': 'Followers', 'count': bitbucket.followers},
        {'name': 'Following', 'count': bitbucket.following},
        {'name': 'Repositories', 'count': bitbucket.total_no_public_repos},
        {'name': 'Account Created', 'count': account_created},

    ]
    return details


def get_blog_details(blog):
    blog_details = get_url_details(blog.url)
    no_of_posts = None
    latest_post = None
    if blog_details:
        no_of_posts = blog_details['no_of_posts']
        latest_post = blog_details['latest_post']
    details = [
        {'name': 'Total Posts', 'count': no_of_posts},
        {'name': 'Latest Post', 'count': latest_post}
    ]
    return details


def get_website_details(website, email):
    details = [
        {'name': 'Alexa Ranking', 'count': get_alexa_ranking(website.url)},
        {'name': 'Email', 'count': email}
    ]
    return details


def get_total_score(mobile_app):
    mobile_app = list(mobile_app)
    for item in mobile_app:
        total_score = item.contribution_score + item.activity_score + item.reputation_score
    average_score = total_score/len(mobile_app)
    return average_score


def get_ios_data(mobile_app):
    mobile_app = list(mobile_app)
    for item in mobile_app:
        total_rating = item.rating_ios
        total_customer_rating_all_version = item.customer_rating_for_all_version_ios
        total_customer_rating_current_version = item.customer_rating_for_current_version_ios
        total_customer_rating = item.total_customer_rating
    average_total_rating = None
    average_customer_rating_all_version = None
    average_customer_rating_current_version = None
    average_customer_rating = None
    length = len(mobile_app)
    if total_customer_rating:
        average_customer_rating = total_customer_rating / length
    elif total_rating is not None:
        average_total_rating = total_rating/length
    elif total_customer_rating_all_version:
        average_customer_rating_all_version = total_customer_rating_all_version/length
    elif total_customer_rating_current_version:
        average_customer_rating_current_version = total_customer_rating_current_version/length

    data = [
        {'name': 'Total Rating', 'count': average_total_rating},
        {'name': 'Customer Rating for all versions', 'count': average_customer_rating_all_version},
        {'name': 'Customer Rating for current version', 'count': average_customer_rating_current_version},
        {'name': 'Customer Rating', 'count': average_customer_rating},
        {'name': 'Apps Link', 'count': length}
    ]
    return data


def get_ios_urls(mobile_app):
    mobile_app = list(mobile_app)
    url_list = [item.app_url for item in mobile_app]
    return url_list


# Android Play Store
def get_android_data(mobile_app):
    mobile_app = list(mobile_app)
    for item in mobile_app:
        total_rating = item.ratings_android
        no_of_installs = item.installs_android
    average_total_rating = None
    average_installs = None
    length = len(mobile_app)
    if total_rating:
        average_total_rating = total_rating/length
    elif no_of_installs:
        average_installs = no_of_installs/length
    data = [
        {'name': 'Total Rating', 'count': average_total_rating},
        {'name': 'App Installs', 'count': average_installs},
        {'name': 'Apps Link', 'count': len(mobile_app)}

    ]
    return data


def get_android_urls(mobile_app):
    mobile_app = list(mobile_app)
    url_list = [item.app_url for item in mobile_app]
    return url_list


def get_download_url(file_name, name):
    connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(AWS_STORAGE_BUCKET_NAME)
    key = Key(bucket)
    if file_name and name:
        splitted_name = name.split('.')
        name = splitted_name[0]
        extension = splitted_name[1]
        key.key = file_name.split('http://filters-api.s3.amazonaws.com/')[1]
        key.make_public()
        response_headers = {
            'response-content-type': 'application/force-download',
            'response-content-disposition': 'attachment; filename="%s"' % name + '.' + extension
        }
        download_url = key.generate_url(604800, query_auth=True, force_http=True, response_headers=response_headers)
        return download_url
    else:
        return None
