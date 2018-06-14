import io
import pytz
import pyocr
import requests
import pyocr.builders
import stackexchange
from tika import parser
from github import Github
from PIL import Image as PI
from wand.image import Image
from datetime import datetime
from wand.exceptions import BlobError
from jarvis.settings.base import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

def get_text(path):
    """
    This Function extracts the text present in documents like pdf, doc etc.
    :param path: path to the document
    :return: (unicode string) parsed text from the document.
    """
    text = parser.from_file(path)  # Apache Tika
    if not text:
        return None
    return text.get('content')


def get_text_via_ocr(pdf, dpi=300):
    """
    This Function extracts the text present in image based resumes.
    :param pdf: string - name of the pdf document
    :param dpi: dpi value, default 300
    :return:
    """
    if '.pdf' in pdf:
        return get_text(pdf)
    finaltext = ''

    try:
        tool = pyocr.get_available_tools()[0]
        lang = 'eng'
    except IndexError:
        return

    req_image = []
    image_pdf = Image(resolution=dpi, filename=pdf)
    image_jpeg = image_pdf.convert('jpeg')

    for img in image_jpeg.sequence:
        img_page = Image(image=img)
        try:
            req_image.append(img_page.make_blob('jpeg'))
        except BlobError:
            return finaltext

    for img in req_image:
        txt = tool.image_to_string(
            PI.open(io.BytesIO(img)),
            lang=lang,
            builder=pyocr.builders.TextBuilder()
        )
        finaltext = finaltext + txt

    del image_jpeg.sequence
    del image_pdf
    del image_jpeg
    del img_page
    del txt

    asciidata = finaltext.encode("ascii", "ignore")
    finaltext = asciidata
    return finaltext


def verify_quality_text(text):
    """
    This function checks if the text extracted is meaningful.
    :param text: string - parsed text obtained from jarvis.resume.
    :return: Boolean - True if quality is upto the match either false.
    """
    lines = text.split('\n')
    num_lines = len(lines)
    long_line = 0
    short_line = 0
    for line in lines:
        if len(line) > 10:
            long_line += 1
        else:
            if len(line) != 0:
                short_line += 1
    if short_line > (num_lines / 2):
        return False
    else:
        return True


# StackOverflow user details
def stackoverflow_user_details(user_id):
    """
    This functions finds the reputation, badges count(gold, silver, bronze), top question and answer tags, account
    creation date, last access date, total number of questions and answers and checks whether the user is a moderator.
    :param user_id: user_id(integer), User id of the candidate
    :return: Returns a dictionary with the candidate details.
    """
    site = stackexchange.Site(stackexchange.StackOverflow)
    user = site.user(user_id)

    # top answer tags
    top_answers_tags = []
    for tags in user.top_answer_tags.fetch():
        top_answers_tags.append(tags.tag_name)

    # top question tags
    top_questions_tags = []
    for tags in user.top_question_tags.fetch():
        top_questions_tags.append(tags.tag_name)

    # total no. of questions
    url = "https://api.stackexchange.com/2.2/users/%s/questions?site=stackoverflow&filter=total" % user_id
    total_no_of_questions = requests.get(url).json()['total']

    # total no. of answers
    url = "https://api.stackexchange.com/2.2/users/%s/answers?site=stackoverflow&filter=total" % user_id
    total_no_of_answers = requests.get(url).json()['total']

    # total no. of unaccepted questions
    url = "https://api.stackexchange.com/2.2/users/%s/questions/unaccepted?site=stackoverflow&filter=total" % user_id
    total_no_of_unaccepted_questions = requests.get(url).json()['total']

    # total no. of unanswered questions
    url = "https://api.stackexchange.com/2.2/users/%s/questions/unanswered?filter=total&site=stackoverflow" % user_id
    total_no_of_unanswered_questions = requests.get(url).json()['total']
    user_details = {}
    try:
        user_details = {
        'website_url': user.website_url
        }
    except AttributeError:
        user_details = {
        'website_url': ''
        }

    user_details = {
        'user_id': user.id,
        'profile_name': user.display_name,
        # To save space, the API does not return null values,
        # instead opting to exclude the field altogether in the returned JSON.
        # Ref: https://api.stackexchange.com/docs/types/user
        'location': getattr(user, 'location', ""),
        'profile_url': user.url,
        'profile_image_url': user.profile_image,
        'reputation': user.reputation,
        'gold_badges_count': user.gold_badges,
        'silver_badges_count': user.silver_badges,
        'bronze_badges_count': user.bronze_badges,
        'top_answer_tags': top_answers_tags,
        'top_question_tags': top_questions_tags,
        'account_creation_date': user.creation_date.replace(tzinfo=pytz.utc),
        'last_access_date': user.last_access_date.replace(tzinfo=pytz.utc),
        'is_moderator': user.is_moderator,
        'total_no_questions': total_no_of_questions,
        'total_no_answers': total_no_of_answers,
        'reputation_change_month': user.json['reputation_change_month'],
        'reputation_change_quarter': user.json['reputation_change_quarter'],
        'reputation_change_year': user.json['reputation_change_year'],
        'total_unanswered_questions': total_no_of_unanswered_questions,
        'total_unaccepted_questions': total_no_of_unaccepted_questions

    }
    return user_details


# Github user details
def github_user_details(user_name):
    """This functions finds the total number of public/private repos, public/private gists, date of account creation,
    update/modification, number of followers, the number of users the candidate is following and details of the repo
    owned by the user - number of stars/forks/watchers, repo creation/update/modification/last pushed date, open issue
    count and repo size.
    :param user_name: (str) github username of the candidate
    :return: returns a dictionary with the candidate details
    """
    git_data = Github(client_id=GITHUB_CLIENT_ID, client_secret=GITHUB_CLIENT_SECRET)
    user = git_data.get_user(user_name.encode('utf-8').strip())

    user_details = {
        'user_id': user.id,
        'user_name': user.login,
        'profile_name': user.name,
        'email': user.email,
        'profile_url': user.html_url,
        'profile_image_url': user.avatar_url,
        'gists_url': user.gists_url[:-10],
        'location': user.location,
        'blog_url': user.blog,
        'company': user.company,
        'hireable': user.hireable,
        'public_repos': user.public_repos,
        'total_private_repos': user.total_private_repos,
        'owned_private_repos': user.owned_private_repos,
        'public_gists': user.public_gists,
        'private_gists': user.private_gists,
        'account_created_at': user.created_at.replace(tzinfo=pytz.utc),
        'last_updated_at': user.updated_at.replace(tzinfo=pytz.utc),
        'last_modified': datetime.strptime(user.last_modified, "%a, %d %b %Y %X %Z").replace(tzinfo=pytz.utc),
        'followers': user.followers,
        'following': user.following,
        # 'repo_details': user_repos,
    }
    return user_details


def bit_bucket_user_details(user_name):
    """
    Function to find the bit bucket user details from bit bucket user name.
    :param user_name: string - bit bucket user name
    :return: dict - dictionary of bit bucket user details
    """
    bit_bucket_url = 'https://api.bitbucket.org/2.0/users/%s' % user_name
    bit_bucket_data = requests.get(bit_bucket_url).json()
    date_conversion = bit_bucket_data['created_on'].split('+')[0]
    account_created_at = date_conversion.split('.')
    # account_created_at = datetime.strptime(date_conversion, "%Y-%m-%dT%X").replace(tzinfo=pytz.utc)
    # account_created_at = date_conversion.split('T')
    account_created_at = datetime.strptime(account_created_at[0], "%Y-%m-%dT%X").replace(tzinfo=pytz.utc)
    # account_created_at = datetime.strptime(account_created_at[0], "%Y-%m-%d").date()
    repo_url = list(bit_bucket_data['links']['repositories'].values())[0]
    total_no_of_repos = requests.get(repo_url).json()['size']
    followers_url = list(bit_bucket_data['links']['followers'].values())[0]
    total_no_of_followers = requests.get(followers_url).json()['size']
    following_url = list(bit_bucket_data['links']['following'].values())[0]
    total_no_of_following = requests.get(following_url).json()['size']
    snippets_url = list(bit_bucket_data['links']['snippets'].values())[0]

    user_details = {
        'user_name': user_name,
        'display_name': bit_bucket_data['display_name'],
        'account_created_at': account_created_at,
        'repo_url': repo_url,
        'total_no_of_repos': total_no_of_repos,
        'followers': total_no_of_followers,
        'following': total_no_of_following,
        'blog_url': bit_bucket_data['website'],
        'profile_url': list(bit_bucket_data['links']['html'].values())[0],
        'snippets_url': snippets_url,
        'location': bit_bucket_data['location'],
    }

    return user_details
