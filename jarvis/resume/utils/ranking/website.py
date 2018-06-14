import re
import sys
import requests
from requests.exceptions import RequestException, HTTPError, BaseHTTPError, ConnectionError, ConnectTimeout, Timeout
from bs4 import BeautifulSoup
from urllib2 import urlparse
from difflib import SequenceMatcher
from .algorithm_base import AlgorithmAbstractClass
from .blog import get_alexa_ranking
import collections
import logging

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

def get_soup(url):
    """
    Get HTML contents from the given website URL.
    """
    try:
        # timeout will minimise max_retries for an invalid url.
        response = requests.get(url, timeout=3)
        response = requests.get(url)
        # Use html5lib parser instead of lxml. Slow but efficient parser.
        return BeautifulSoup(response.content, "html5lib")
    except RequestException as e:
        print(e)
        logger.debug(e)
        logger.debug("Connection Timed Out. The site: {} didn't respond".format(url))
    return ""


class WebsiteEnum:
    """ENUM class contains constants used for calculation of Website Score.
       Changing the value of the constants will change the behavious of Website Algorithm.
    """
    # Website Reputation
    WEBSITE_REPUTATION_RANGE_TYPE = collections.namedtuple(
        'WEBSITE_REPUTATION_RANGE_TYPE', 'low high'
    )

    WEBSITE_REPUTATION_MAPPING = {
        WEBSITE_REPUTATION_RANGE_TYPE(1, 500000): 0.2,
        WEBSITE_REPUTATION_RANGE_TYPE(500001, 10000000): 0.16,
        WEBSITE_REPUTATION_RANGE_TYPE(10000001, 15000000): 0.12,
        WEBSITE_REPUTATION_RANGE_TYPE(15000001, 20000000): 0.08,
        WEBSITE_REPUTATION_RANGE_TYPE(20000001, 25000000): 0.04,
        WEBSITE_REPUTATION_RANGE_TYPE(25000001, sys.maxsize): 0.02,

    }


class WebsiteScore(AlgorithmAbstractClass):
    """
    Calculate score for website
    :param : Takes email address and blog urls as an input
    :returns : Score
    """
    def __init__(self, email_address, blog_urls):
        self.score = 0
        self.email_address = email_address
        self.blog_urls = blog_urls
        self._url = self.blog_urls[0]
        self._contribution_score = 0
        self._activity_score = 0
        self._reputation_score = 0
        self._alexa_ranking = 0
        self._total_score = 0

    def _get_email_match_score(self):
        """
        Check if emails are identical
        """
        EMAIL_REGEX_PATTERN = (
            "([a-zA-Z0-9_.+-]+\s*(\@|\[at]|\[@])\s*[a-zA-Z0-9-]+\s*" + "(\.|\[.]|\[dot])\s*[a-zA-Z0-9-.]+)"
        )
        if self.blog_urls or (len(self.blog_urls) > 0):
            website = self.blog_urls[0]
        else:
            return
        if '//' not in website:
            website = '%s%s' % ('http://', website)
        scraped_email = re.findall(EMAIL_REGEX_PATTERN, str(get_soup(website)))
        if scraped_email:
            scraped_email = scraped_email[0][0].split("@")[0]
            matching_ratio = SequenceMatcher(
                None, scraped_email, self.email_address
            ).ratio()
            return matching_ratio
        return None

    def get_scraped_email(self):
        EMAIL_REGEX_PATTERN = (
            "([a-zA-Z0-9_.+-]+\s*(\@|\[at]|\[@])\s*[a-zA-Z0-9-]+\s*" + "(\.|\[.]|\[dot])\s*[a-zA-Z0-9-.]+)"
        )
        if self.blog_urls or (len(self.blog_urls) > 0):
            website = self.blog_urls[0]
        else:
            return
        if '//' not in website:
            website = '%s%s' % ('http://', website)
        scraped_email = re.findall(EMAIL_REGEX_PATTERN, str(get_soup(website)))
        return scraped_email

    def _get_email_and_domain_name_match_ratio(self):
        """
        Get the matching ratio of sequences
            1. Compare sequences of email address and website domain name
            2. Return the matching ratio
        """
        if self.blog_urls or (len(self.blog_urls) > 0):
            website = self.blog_urls[0]
            email_id = self.email_address.split("@")[0]
            self._contribution_score = SequenceMatcher(
                None, email_id, website
            ).ratio()

    def get_contribution_score(self):
        """Calculates Contribution Score based on Email Matching with the website URL.
        """
        # total score 0.6
        matching_ratio = self._get_email_match_score()
        if not matching_ratio:
            self._get_email_and_domain_name_match_ratio()
            return self._contribution_score
        self._contribution_score = matching_ratio*0.8
        return float("{0:.2f}".format(self._contribution_score))

    def get_reputation_score(self):
        """Calculates Reputation Score based on Alexa Ranking."""
        self._alexa_ranking = get_alexa_ranking(self._url)
        # total score = 0.2
        for key in WebsiteEnum.WEBSITE_REPUTATION_MAPPING:
            if key.low <= self._alexa_ranking <= key.high:
                return WebsiteEnum.WEBSITE_REPUTATION_MAPPING[key]
        return 0

    def get_activity_score(self):
        return 0

    def get_total_score(self):
        """Total Website Score: Sum of Reputation, Contribution and Activity Score."""
        self._total_score = self.get_activity_score() + self.get_contribution_score() + self.get_activity_score()
        return float("{0:.2f}".format(self._total_score))

