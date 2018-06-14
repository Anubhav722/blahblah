from bs4 import BeautifulSoup
import urllib2
from datetime import datetime
from .algorithm_base import AlgorithmAbstractClass
import sys
import collections


class ItunesEnum:
    # Customer Rating for Current Version
    APP_RATING_RANGE_TYPE = collections.namedtuple(
        "APP_CURRENT_RANGE_TYPE", "high low"
    )

    APP_RATING_CURRENT_VERSION_MAPPING = {
        APP_RATING_RANGE_TYPE(sys.maxsize, 400): 0.2,
        APP_RATING_RANGE_TYPE(399, 350): 0.15,
        APP_RATING_RANGE_TYPE(349, 300): 0.1,
        APP_RATING_RANGE_TYPE(299, 250): 0.05,
        APP_RATING_RANGE_TYPE(249, 1): 0.025,
    }

    APP_RATING_ALL_VERSION_MAPPING = {
        APP_RATING_RANGE_TYPE(sys.maxsize, 1000): 0.2,
        APP_RATING_RANGE_TYPE(999, 700): 0.15,
        APP_RATING_RANGE_TYPE(699, 400): 0.1,
        APP_RATING_RANGE_TYPE(399, 100): 0.05,
        APP_RATING_RANGE_TYPE(99, 1): 0.025,
    }

    APP_RATING_TOTAL_MAPPING = {
        APP_RATING_RANGE_TYPE(5, 4.5): 0.3,
        APP_RATING_RANGE_TYPE(4.5, 4.0): 0.25,
        APP_RATING_RANGE_TYPE(4.0, 3.5): 0.2,
        APP_RATING_RANGE_TYPE(3.5, 3): 0.15,
        APP_RATING_RANGE_TYPE(3, 2.5): 0.1,
        APP_RATING_RANGE_TYPE(2.5, 0): 0.05,
    }

    ACTIVITY_SCORE_RANGE_MAX = 0.3
    ACTIVITY_SCORE_RANGE_MIN = 0.15
    MONTHS_PASSED = 6
    CONTRIBUTION_SCORE_RANGE_MAX = 0.2
    CONTRIBUTION_SCORE_RANGE_MIN = 0.05


class ItunesScore(AlgorithmAbstractClass):
    def __init__(self, app_url, user_name):
        self._app_url = app_url
        self._app_developer_name = ''
        self._app_rating = 0
        self._customer_rating = 0
        self._app_name = ''
        self.developer_name = ''
        self._content = ''
        self._soup = ''
        self._app_details = ''
        self._body = ''
        self.no_of_customer_rating_for_current_version = None
        self.no_of_customer_rating_for_all_version = None
        self.total_customer_rating = None
        self.rating = None
        self.months_passed = 0
        self.app_last_updated_date = None
        self._user_name = user_name.lower()
        # scores
        self.total_score = 0
        self.activity_score = 0
        self.contribution_score = 0
        self.reputation_score = 0
        self.developer_score = 0

    def _extract(self):
        """
        Scrapping and calculating app details.
        :return:
        """
        self._content = urllib2.urlopen(self._app_url).read()
        self._soup = BeautifulSoup(self._content, 'lxml')
        self._body = self._soup.body
        self._today = datetime.today().date()
        try:
            self.app_details = self._body.find_all('div', class_='left')[1]
            self.app_name = self.app_details.h1.string
            self.developer_name = self.app_details.h2.string.split('By')[1].strip().lower()
            self.app_last_updated_date = self._body.find_all('li', class_='release-date')[0].contents[1].contents[0].strip()
            self.rating = self._body.find_all('div', class_='app-rating')[0].contents[0].contents[0].strip().split('for the following:')[0].strip().split('Rated')[1].strip()[0]
            self.no_of_customer_rating_for_current_version = int(self._body.find_all('span', class_='rating-count')[0].contents[0].split('Ratings')[0].strip())
            self.no_of_customer_rating_for_all_version = int(self._body.find_all('span', class_='rating-count')[1].contents[0].split('Ratings')[0].strip())
            self.total_customer_rating = float(self._body(itemprop='ratingValue')[0].contents[0])
        except IndexError:
            print('App Details not found.')
            return
        try:
            self._last_updated_data_datetime = datetime.strptime(self.app_last_updated_date, '%d %B %Y').date()
        except ValueError:
            self._last_updated_data_datetime = datetime.strptime(self.app_last_updated_date, "%b %d, %Y").date()
        except Exception:
            return
        try:
            self.months_passed = (self._today - self._last_updated_data_datetime).days/30
        except Exception:
            self.months_passed = 0

    def get_activity_score(self):
        """Activity Score based on months passed
        """
        # total score 0.3
        self._extract()
        # calculating activity score
        if self.months_passed <= ItunesEnum.MONTHS_PASSED:
            self.activity_score = ItunesEnum.ACTIVITY_SCORE_RANGE_MAX
        else:
            self.activity_score = ItunesEnum.ACTIVITY_SCORE_RANGE_MIN
        return self.activity_score

    def get_contribution_score(self):
        """
        Contribution Score calculated on the basis of developer name.
        """
        # total score 0.2
        self._extract()
        if self.developer_name == self._user_name:
            self.contribution_score = ItunesEnum.CONTRIBUTION_SCORE_RANGE_MAX
        else:
            self.contribution_score = ItunesEnum.CONTRIBUTION_SCORE_RANGE_MIN
        return self.contribution_score

    def get_reputation_score(self):
        """Reputation score calculated on the basis of Customer rating for the current version,
        all version and Total Rating given by customer."""
        self._extract()
        app_rating_score_current = 0
        app_rating_score_all = 0
        total_customer_rating_score = 0

        # calculating app rating score
        if self.no_of_customer_rating_for_all_version > 0:
            for key in ItunesEnum.APP_RATING_ALL_VERSION_MAPPING:
                if key.low < self.no_of_customer_rating_for_all_version <= key.high:
                    app_rating_score_all = ItunesEnum.APP_RATING_ALL_VERSION_MAPPING[key]

        if self.no_of_customer_rating_for_current_version > 0:
            for key in ItunesEnum.APP_RATING_CURRENT_VERSION_MAPPING:
                if key.low < self.no_of_customer_rating_for_current_version <= key.high:
                    app_rating_score_current = ItunesEnum.APP_RATING_CURRENT_VERSION_MAPPING[key]

        for key in ItunesEnum.APP_RATING_TOTAL_MAPPING:
            if key.low < self.total_customer_rating <= key.high:
                total_customer_rating_score = ItunesEnum.APP_RATING_TOTAL_MAPPING[key]

        self.reputation_score = app_rating_score_all + app_rating_score_current + total_customer_rating_score
        return self.reputation_score

    def get_total_score(self):
        """ Getting final app score"""
        self.total_score = self.get_activity_score() + self.get_contribution_score() + self.get_reputation_score()
        return float("{0:.2f}".format(self.total_score))


