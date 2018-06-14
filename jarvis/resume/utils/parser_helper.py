
# external imports
import re
from string import digits
from github import Github
from django.contrib.admin.utils import NestedObjects
from django.db import DEFAULT_DB_ALIAS
from django.db.models.fields.related import ForeignKey

import unicodedata
from unidecode import unidecode
from .url_finder import url_regex
import tldextract

# url summarizer import
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from urlparse import urlparse
from simhash import Simhash
from jarvis.resume.constants import (
    EMAIL_REGEX, INDIA_COUNTRY_CODE, INDIAN_PHONE_NUM_REG,
    INDIAN_PHONE_NUMBER_LENGTH
)

# settings
from jarvis.settings.base import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from celery.contrib import rdb
# url_list
from .url_list import repository_urls, coding_urls, blog_urls, forum_urls, social_urls, blacklist_urls, app_urls

disciplines_mapping = {
    "ph.d": ["phd"],
    "m.b.a": ["mba"],
    "m.c.a": ["mca"],
    "b.c.a": ["bca"],
}

disciplines = [
    ("b.e", "bachelor of engineering"),
    ("b.tech", "bachelor of technology"),
    ("m.tech", "master of technology"),
    ("m.sc", "master of science"),
    ("m.s", "master of science"),
    ("b.sc", "bachelor of science"),
    ("ph.d", "doctrate"),
    ("mba", "master of business administration"),
    ("mca", "master of computer application"),
    ("bca", "bachelor of computer application"),
    ("b.s", "bachelor of science"),
    ("m.phil", "master of philosophy"),
    ("b.a", "bachelor of arts"),
    ("m.a", "master of arts"),
]

# degrees = [(short_form, long_form, [aliases])]
degrees = [
    ("ph.d", "doctrate", ["ph.d.", "phd", "dr."]),
    ("b.a", "bachelor of arts", ["b.a."]),
    ("b.c.a", "bachelor of computer application", ["b.c.a.", "bca"]),
    ("b.e", "bachelor of engineering", ["b.e."]),
    ("b.sc", "bachelor of science", ["b.s", "b.sc.", "bsc"]),
    ("b.tech", "bachelor of technology", ["b.tech.", "btech"]),
    ("m.a", "master of arts", []),
    ("m.tech", "master of technology", ["m.tech.", "mtech"]),
    ("m.sc", "master of science", ["m.s", "m.sc.", "msc"]),
    ("m.b.a", "master of business administration", ["m.b.a.", "mba"]),
    ("m.c.a", "master of computer application", ["m.c.a.", "mca"]),
    ("m.phil", "master of philosophy", ["m.phil.", "mphil"]),
]

def hash_distance(sim_hash_one, sim_hash_two):
    """
    Calculates hamming distance between two sim hashes.
    :param sim_hash_one: long - sim hash
    :param sim_hash_two: long - sim hash
    :return: (int) returns hamming distance.
    """
    f = 128
    x = (sim_hash_one ^ sim_hash_two) & ((1 << f) - 1)
    ans = 0
    while x:
        ans += 1
        x &= x - 1
    return ans

"""
Phone and Email Sections
"""

def get_nums(text):
    """
    Fetches phone numbers from the text obtained from the resume.
    :param text: (unicode string) parsed text from the resume
    :return: a list of possible phone numbers.
    """
    text = text.replace(' ', '')
    phone_nums = get_standard_indian_format_number(text)
    if len(phone_nums) == 0:
        return None
    else:
        return ",".join(phone_nums)

def get_matched_degrees(text):
    res = list()
    content_set = set(text.lower().split())
    for content in content_set:
        for k, v, aliases in degrees:
            need_to_match = aliases.extend([k, v])
            if content in need_to_match:
                res.append({"short_name": k, "long_name": v})
    return res

def get_course_discipline(text):
    res = []
    text = text.lower()
    for d in disciplines:
        if ((d[0] in text) or (d[1] in text)) and d[0] not in res:
            res.append({"short_name": d[0], "long_name": d[1]})
    return res

def get_email(text):
    """
    Fetches all emails from the text obtained from the resume.
    :param text:(unicode string) parsed text from the resume
    :return: a list of possible emails
    """
    emails = list()
    result = re.search(EMAIL_REGEX, text)

    if result:
        emails.append(result.group())
        return emails
    return None

"""
GitHub + LinkedIn SECTION
"""


def get_linkedin(text):
    """
    Fetches LinkedIn url from the text obtained from the resume.
    :param text: (unicode string) parsed text from the resume
    :return: a list of LinkedIn url
    """
    linkedin_url = []
    linkedins = re.findall('.*[\w\.-]+linkedin[\w\.-]+.*', text)

    if len(linkedins) == 0:
        return None
    else:
        #    print linkedins
        for line in linkedins:
            line = line.split(" ")
            for word in line:
             #           print line
                if 'linkedin.com' in word:
                    linkedin_url.append(word)

        return linkedin_url


def get_github(text):
    """
    Fetches GitHub and GitHub's gist urls from the text obtained from the resume.
    :param text:(unicode string) parsed text from the resume.
    :return: a list of GitHub and Gist urls
    """
    github_url = []
    githubs = re.findall('.*[\w\.-]*github[\w\.-]*.*', text)

    if len(githubs) == 0:
        return None
    else:

        for line in githubs:
            line = line.split(" ")
            for word in line:
                if 'github.com' in word:
                    github_url.append(word)

        return github_url


def get_id_from_linkedin_url(text):
    """
    Fetches LinkedIn id from LinkedIn url
    :param text:(unicode string) parsed text from the resume
    :return: (string) user LinkedIn id.
    """
    list_urls = get_linkedin(text)
    for url in list_urls:
        if 'pub' in url:
            loc = url.find('/pub/')
            matched = url[loc + 5:]
            slash_loc = matched.find('/')
            if slash_loc == -1:
                return matched
            else:
                return matched[:slash_loc]

        else:
            loc = url.find('/in/')
            matched = url[loc + 4:]
            return matched.split('/')[0]


def get_username_from_github_url(text):
    """
    Fetches GitHub username from GitHub url
    :param text: (unicode string) parsed text from the resume
    :return: (string) GitHub username.
    """
    githubs = get_github(text)
    if githubs is None:
        return None
    for text_blob in githubs:
        loc = text_blob.find('github.com/')
        if loc > -1:

            matched = text_blob[loc + 11:]
            slash_loc = matched.find('/')
            if slash_loc == -1:
                return matched
            else:
                return matched[:slash_loc]


"""
Name Section
"""


def get_name_data_from_email(parsed_text):
    """
    Fetches username / name / id from email(without @domain.com etc.)
    :param parsed_text: (unicode string) parsed text from the resume.
    :return: a list of names present in the email.
    """
    list_emails = get_email(parsed_text)
    if list_emails is None:
        return None
    list_name_data = []
    for email in list_emails:
        pos = email.find('@')
        if pos == -1:
            return None
        else:
            email = email[0:pos].replace(".", "")
            email = email.replace("_", "")

            list_name_data.append(email.encode(
                'utf-8').translate(None, digits))
    return list_name_data


def _get_all_substrings_in_email(input_string):
    length = len(input_string)
    return [input_string[i:j + 1] for i in range(length) for j in range(i, length)]


def get_name_candidates_from_email(parsed_text):
    """
    Gets possible combination of names from the email address
    :param parsed_text: (unicode string) parsed text from the resume.
    :return: a list of possible combination of names.
    """
    banned = ['the', 'and']
    string_list = []
    list_name_data = get_name_data_from_email(parsed_text)
    if list_name_data is None:
        return None
    for namestring in list_name_data:
        sub_strings = _get_all_substrings_in_email(namestring)
        filtered_sub_strings = [
            substring for substring in sub_strings if ((len(substring) > 2) and substring not in banned)]
        string_list = string_list + filtered_sub_strings
    return string_list


def get_name(parsed_text):
    """
    Fetches name of the candidate from the parsed text.
    :param parsed_text:(unicode string) parsed text fromt the resume.
    :return: a list of possible candidate names.
    """
    original_text = parsed_text
    text = ''
    substrings = get_name_candidates_from_email(parsed_text.lower())
    name_string = get_name_data_from_email(parsed_text.lower())
    if name_string is None:
        return None
    parsed_lines = parsed_text.split('\n')
    names = []

    parsed_lines = [x.lower() for x in parsed_lines]
    for string in substrings:
        try:
            sre = re.search(r"\b%s\b" % string, str(parsed_lines))
        except:
            pass
        if sre is not None:
            if len(names) == 0:
                names.append(sre.group())
            else:
                for name in names[:]:
                    if string in name:
                        pass
                    elif name in string:
                        for big_string in name_string:
                            if big_string == string:
                                pass
                            else:
                                if name in names:
                                    names.remove(name)
                    else:
                        names.append(sre.group())
    if len(names) > 0:
        return names
    else:
        first_line = original_text.split('\n')[0]
        match = compare_email_line(text.lower(), first_line)
        if match:
            if 'resume' not in first_line:
                first_line = first_line.decode('utf-8', 'ignore')
                return first_line
        return None


def compare_email_line(parsed_text, first_line):
    names_cand = get_name_candidates_from_email(parsed_text)
    if names_cand is None:
        return None
    first_line = first_line.lower()
    for names in names_cand:
        if names in first_line:
            return True
        else:
            return False


# extraction of repository details
def get_repo_details(user_name, repo_name):
    """

    :param user_name: (str) - github username of the candidate
    :param repo_name: (str) - repo name created by the above mentioned user.
    :return: (dict) - returns a dictionary with all the details of a repo.
    """
    github_data = Github(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
    repo = github_data.get_user(user_name).get_repo(repo_name)

    repo_details = {
        'id': repo.id,
        'name': repo.name,
        'url': repo.url,
        'owner_username': repo.owner.login,
        'organization': repo.organization,
        'language': repo.language,
        'is_forked': repo.fork,
        'no_of_stars': repo.stargazers_count,
        'no_of_forks': repo.forks_count,
        'no_of_watchers': repo.watchers_count,
        'repo_created_at': repo.created_at.date(),
        'repo_last_updated': repo.updated_at.date(),
        'last_pushed_at': repo.pushed_at.date(),
        'open_issues_count': repo.open_issues_count,
        'repo_size': repo.size,
    }
    return repo_details


# get GitHub username
def get_github_username(text):
    """
    Finds the github url of a candidate
    :return: the github username of the candidate
    """
    github_url = []
    github_data = re.findall('.*[\w\.-]*github[\w\.-]*.*', text)

    if len(github_data) == 0:
        return None
    else:
        for data in github_data:
            data = data.split(' ')
            for word in data:
                # print data
                if 'github.com' in word:
                    github_url.append(word)

    for url in github_url:
        location = url.find('github.com/')
        if location > -1:
            match = url[location + 11:]
            slash_location = match.find('/')
            match = unicodedata.normalize('NFKC', match).strip()
            if slash_location == -1:
                return match


# get StackOverflow user id
def get_stackoverflow_userid(text):
    """
    Finds the stackoverflow userid of a candidate
    :return: stackoverflow user id
    """
    stackoverflow_url = []
    stackoverflow_data = re.findall('.*[\w\.-]*stackoverflow[\w\.-]*.*', text)

    if len(stackoverflow_data) == 0:
        return None
    else:
        for data in stackoverflow_data:
            data = data.split(' ')
            for word in data:
                if 'stackoverflow.com/users/' in word:
                    stackoverflow_url.append(word)
    for url in stackoverflow_url:
        location = url.find('stackoverflow.com/users/')
        if location > -1:
            match = url[location + 24:]
            slash_location = match.find('/')
            if slash_location == -1:
                return match
            else:
                return match[:slash_location]


# get StackOverflow username
def get_stackoverflow_username(text):
    """
    Finds the stackoverflow userid of a candidate
    :return: stackoverflow user id
    """
    stackoverflow_url = []
    stackoverflow_data = re.findall('.*[\w\.-]*stackoverflow[\w\.-]*.*', text)

    if len(stackoverflow_data) == 0:
        return None
    else:
        for data in stackoverflow_data:
            data = data.split(' ')
            for word in data:
                if 'stackoverflow.com/users/' in word:
                    stackoverflow_url.append(word)
    for url in stackoverflow_url:
        location = url.find('stackoverflow.com/users/')
        if location > -1:
            match = url[location + 24:]
            slash_location = match.find('/')
            match = unicodedata.normalize('NFKC', str(match)).strip()
            if slash_location == -1:
                return match
            else:
                return match[slash_location+1:]


def get_urls(text):
    """
    Find all the urls inside a Resume
    :param text: is the text extracted from pdf
    :return: a list of all the urls present in the resume.
    """

    text = unidecode(text)
    # urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    urls = re.findall(url_regex, text)
    return urls


def url_summary(url):
    """
    Fetches 20 summarized sentences from the url provided.
    :param url: is a website url
    :return: an object of Stemmer class.
    """
    LANGUAGE = 'english'
    sentence_count = 20
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sentences = []
    for sentence in summarizer(parser.document, sentence_count):
        sentences.append(sentence)

    return sentences


def url_categories(urls):
    """
    Categorize the type of url from a list of urls.
    :param urls:(list)
    :return: a dictionary with the categorized urls.
    """
    social = []
    coding = []
    forums = []
    contributions = []
    blog = []
    apps = []
    others = []
    for item in urls:
        tld = tldextract.extract(item)
        tld_extract = tld.domain + '.' + tld.suffix
        item_parse = urlparse(item)
        if item_parse.scheme == '':
            item = 'http://' + item_parse.path
        if tld_extract in blacklist_urls:
            pass
        elif tld_extract in repository_urls:
            contributions.append(item)
        elif tld_extract in coding_urls:
            coding.append(item)
        elif tld_extract in blog_urls or 'blog' in item:
            blog.append(item)
        elif tld_extract in forum_urls:
            forums.append(item)
        elif tld_extract in social_urls:
            social.append(item)
        elif item_parse.netloc in app_urls:
            apps.append(item)
        else:
            others.append(item)

    categories = {'contributions': contributions, 'forums': forums, 'social': social, 'blog': blog, 'coding': coding,
                   'apps': apps, 'others': others}
    return categories


def get_url_response(categories):
    """
    Change the url categories to a readable format
    :param categories: is a dictionary of items
    :return: list of dictionaries
    """
    dump_data = {}
    url_response = []
    urls_unique = set()
    for key, value in list(categories.items()):
        for item in value:
            item = item.lower()
            item_parse = urlparse(item)
            if item_parse.scheme == '':
                item = 'http://' + item_parse.path
            if value and (item not in urls_unique):
                dump_data["type"] = key
                dump_data["name"] = item
                url_response.append(dump_data)
                dump_data = {}
                urls_unique.add(item)

    return url_response


def get_bit_bucket_url(contribution_urls):
    """
    This Function finds the bit bucket url from a list of urls
    :param contribution_urls: list of urls
    :return: url -  bit bucket url
    """

    for url in contribution_urls:
        if 'bitbucket.com' in url or 'bitbucket.org' in url:
            return url
        else:
            return 'No Url Found'


def get_bitbucket_username(bitbucket_url):
    """
    This function extracts bit bucket username from bit bucket url.
    :param bitbucket_url: url - bit bucket url
    :return: string - username extracted from bit bucket url
    """
    location = bitbucket_url.find('bitbucket.org/')
    bitbucket_username = bitbucket_url[location + 14:]
    slash_location = bitbucket_username.find('/')
    if slash_location == -1:
        return bitbucket_username
    else:
        return bitbucket_username[:slash_location]


def get_sim_hash_for_resume_content(content):
    """
    This function calculates sim hash of the text parsed from a resume.
    :param content: string - parsed text from jarvis.resume.
    :return: sim hash object.
    """
    if not content:
        return ''

    threshold_bit_difference = 3  # means the near duplicate values differ in at most 3-bit position
    content = content.lower()
    content = re.sub(r'[^\w]+', '', content)
    hashed_content = [
        content[i:i + threshold_bit_difference] for i in range(max(len(content) - threshold_bit_difference + 1, 1))
    ]
    hash_object = Simhash(hashed_content)
    return hash_object


def check_hamming_distance(list_hash_values, new_hash_value):
    """
    This Function Checks for if the newly generated hash value from the resume matches with any hash value in
    the database
    :param list_hash_values(list) - list of all the hash values from the database
    :param new_hash_value(long) - newly generated hash value from the uploaded resume.
    :returns:
    """
    hamming_distance_threshold = 1
    hamming_distance = []
    for value in list_hash_values:
        hamming_distance.append(hash_distance(int(value), new_hash_value))

    for i, distance in enumerate(hamming_distance):
        if distance < hamming_distance_threshold:
            return True, list_hash_values[i]
    return False, 0


def duplicate(obj, value=None, field=None, duplicate_order=None):
    """
    Duplicate all related objects of obj setting
    field to value. If one of the duplicate
    objects has an FK to another duplicate object
    update that as well. Return the duplicate copy
    of obj.
    duplicate_order is a list of models which specify how
    the duplicate objects are saved. For complex objects
    this can matter. Check to save if objects are being
    saved correctly and if not just pass in related objects
    in the order that they should be saved.
    """
    collector = NestedObjects(using=DEFAULT_DB_ALIAS)
    collector.collect([obj])
    collector.sort()
    related_models = list(collector.data.keys())
    data_snapshot = {}
    for key in list(collector.data.keys()):
        data_snapshot.update({key: dict(list(zip([item.pk for item in collector.data[key]], [item for item in collector.data[key]])))})
    root_obj = None

    if duplicate_order is None:
        duplicate_order = reversed(related_models)

    for model in duplicate_order:
        # Find all FKs on model that point to a related_model.
        fks = []
        for f in model._meta.fields:
            if isinstance(f, ForeignKey) and f.rel.to in related_models:
                fks.append(f)
        # Replace each `sub_obj` with a duplicate.
        if model not in collector.data:
            continue
        sub_objects = collector.data[model]
        for obj in sub_objects:
            for fk in fks:
                fk_value = getattr(obj, "%s_id" % fk.name)
                # If this FK has been duplicated then point to the duplicate.
                fk_rel_to = data_snapshot[fk.rel.to]
                if fk_value in fk_rel_to:
                    dupe_obj = fk_rel_to[fk_value]
                    setattr(obj, fk.name, dupe_obj)
            # Duplicate the object and save it.
            obj.id = None
            if field is not None:
                setattr(obj, field, value)
            obj.save()
            if root_obj is None:
                root_obj = obj
    return root_obj

# :: Expected behavior ::
# It should return list of phone numbers with indian
# standard format, after parsing of any text.
def get_standard_indian_format_number(text):
    numbers_list = list()
    phone_numbers = re.finditer(INDIAN_PHONE_NUM_REG, text)
    for match in phone_numbers:
        original_number = match.group(1)[-INDIAN_PHONE_NUMBER_LENGTH:]
        numbers_list.append(INDIA_COUNTRY_CODE + original_number)

    return numbers_list
