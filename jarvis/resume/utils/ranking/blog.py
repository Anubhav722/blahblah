import sys
import seolib
import feedparser
import collections
from urlparse import urlparse
from .algorithm_base import AlgorithmAbstractClass
from time import mktime
from datetime import datetime


# Helper Functions

def get_alexa_ranking(url):
    """Get Alexa website ranking"""
    ranking = None
    if ('http://' or 'https://') in url:
        ranking = seolib.get_alexa(url)
    else:
        if url:
            parsed_url = urlparse(url)
            final_url = 'http://' + parsed_url.path
            ranking = seolib.get_alexa(final_url)
    return ranking


def get_url_feed(url):
    feed = feedparser.parse(url)
    entries = feed['entries']
    details = {}
    if entries:
        # taking the latest post
        last_updated = entries[0]['updated_parsed']
        updated_date = (datetime.fromtimestamp(mktime(last_updated))).date()
        no_of_posts = len(entries)
        details['no_of_posts'] = no_of_posts
        details['latest_post'] = updated_date
        details['url'] = url
    return details


def get_url_details(url):
    """Blog details.
    :param url
    :returns a dictionary with latest post count(up to 20) and last_updated for the latest post.
    """
    if 'medium.com/feed' in url:
        final_url = url
        feed = get_url_feed(final_url)
        return feed
    elif 'medium.com' in url:
        parsed_url = urlparse(url)
        path = parsed_url.path.split('/')
        if ('http://' or 'https://') in url:
            final_url = parsed_url.scheme + '://' + parsed_url.netloc + '/feed' + parsed_url.path
            feed = get_url_feed(final_url)
            return feed
        else:
            final_url = 'http://' + path[0] + '/feed/' + path[1]
            feed = get_url_feed(final_url)
            return feed
    elif not ('feed' in url) and not ('rss' in url):
        if url[-1] == '/':
            final_url = url + 'feed'
            feed = get_url_feed(final_url)
            if feed == {}:
                final_url = url + 'rss'
                feed = get_url_feed(final_url)
                return feed
        elif url[-1] != '/':
            final_url = url + '/feed'
            feed = get_url_feed(final_url)
            if feed == {}:
                final_url = url + '/rss'
                feed = get_url_feed(final_url)
                return feed

    return get_url_feed(url)


class BlogEnum:
    # Blog Contribution
    BLOG_CONTRIBUTION_RANGE_TYPE = collections.namedtuple(
        'BLOG_CONTRIBUTION_RANGE_TYPE', "high low"
    )
    BLOG_CONTRIBUTION_MAPPING = {
        BLOG_CONTRIBUTION_RANGE_TYPE(sys.maxsize, 18): 0.4,
        BLOG_CONTRIBUTION_RANGE_TYPE(18, 15): 0.34,
        BLOG_CONTRIBUTION_RANGE_TYPE(15, 12): 0.28,
        BLOG_CONTRIBUTION_RANGE_TYPE(12, 9): 0.22,
        BLOG_CONTRIBUTION_RANGE_TYPE(9, 6): 0.16,
        BLOG_CONTRIBUTION_RANGE_TYPE(6, 3): 0.1,
        BLOG_CONTRIBUTION_RANGE_TYPE(3, 0): 0.04,
    }

    # Blog Reputation
    BLOG_REPUTATION_RANGE_TYPE = collections.namedtuple(
        'BLOG_REPUTATION_RANGE_TYPE', 'low high'
    )

    BLOG_REPUTATION_MAPPING = {
        BLOG_REPUTATION_RANGE_TYPE(1, 500000): 0.2,
        BLOG_REPUTATION_RANGE_TYPE(500001, 10000000): 0.16,
        BLOG_REPUTATION_RANGE_TYPE(10000001, 15000000): 0.12,
        BLOG_REPUTATION_RANGE_TYPE(15000001, 20000000): 0.08,
        BLOG_REPUTATION_RANGE_TYPE(20000001, 25000000): 0.04,
        BLOG_REPUTATION_RANGE_TYPE(25000001, sys.maxsize): 0.02,

    }

    # Blog Activity
    BLOG_ACTIVITY_RANGE_TYPE = collections.namedtuple(
        'BLOG_ACTIVITY_RANGE_TYPE', 'low high'
    )

    BLOG_ACTIVITY_MAPPING = {
        BLOG_ACTIVITY_RANGE_TYPE(0, 8): 0.4,
        BLOG_ACTIVITY_RANGE_TYPE(9, 17): 0.34,
        BLOG_ACTIVITY_RANGE_TYPE(18, 26): 0.28,
        BLOG_ACTIVITY_RANGE_TYPE(27, 34): 0.22,
        BLOG_ACTIVITY_RANGE_TYPE(35, 42): 0.16,
        BLOG_ACTIVITY_RANGE_TYPE(42, sys.maxsize): 0.1,

    }


class BlogScore(AlgorithmAbstractClass):
    """
    Calculate score of the details obtained from url_details functions
    :param : takes dictionary as an input
    :returns : return score for blog details.
    """
    def __init__(self, url_details):
        self.total_score = 0
        self.no_of_posts = 0
        self._url = ''
        self._alexa_ranking = 0
        self.contribution_score = 0
        self.reputation_score = 0
        self._url_details = url_details
        self.days_passed = 0

    def _extract(self):
        """
        Extract Blog details like no. of post counts, Date of latest post
        """
        if ('latest_post' and 'no_of_posts' and 'url') in list(self._url_details.keys()):
            self._latest_post_date = self._url_details['latest_post']
            self.no_of_posts = self._url_details['no_of_posts']
            self._url = self._url_details['url']
            self.today_date = datetime.today().date()
            self.latest_post_date = datetime.today().date()
            self.days_passed = (self.today_date - self.latest_post_date).days

    def get_contribution_score(self):
        """
        Calculating Blog Contribution Score based on no. of posts
        """
        self._extract()
        for key in BlogEnum.BLOG_CONTRIBUTION_MAPPING:
            if key.high >= self.no_of_posts > key.low:
                return BlogEnum.BLOG_CONTRIBUTION_MAPPING[key]
        return 0

    def get_reputation_score(self):
        """
        Calculates Blog Reputation Score on the basis on alexa ranking
        """
        self._extract()
        self._alexa_ranking = get_alexa_ranking(self._url)
        # total score = 0.2
        for key in BlogEnum.BLOG_REPUTATION_MAPPING:
            if key.low <= self._alexa_ranking <= key.high:
                return BlogEnum.BLOG_REPUTATION_MAPPING[key]
        return 0

    def get_activity_score(self):
        """
        Activity Score calculated on the basis on date of latest post
        :return: float
        """
        self._extract()
        for key in BlogEnum.BLOG_ACTIVITY_MAPPING:
            if key.low <= self.days_passed <= key.high:
                return BlogEnum.BLOG_ACTIVITY_MAPPING[key]
        return 0

    def get_total_score(self, activity_score, contribution_score, reputation_score):
        """Total score: Sum of activity, contribution and reputation score"""
        total_score = activity_score + contribution_score + reputation_score
        return total_score
