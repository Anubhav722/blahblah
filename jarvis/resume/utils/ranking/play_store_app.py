import re, requests
from datetime import datetime
from bs4 import BeautifulSoup
from .algorithm_base import AlgorithmAbstractClass
import logging

from urllib2 import HTTPError, URLError, urlopen


class PlayStoreAppRating(AlgorithmAbstractClass):
    """
    Play Store App Algorithm:
        1. `Ratings`: As it is.
        2. `Updated`:
            - If app is updated within 6 months: Score will be 2.5 else 1.5
        3. `Installs`:
            - If total installs are in between 100 - 500 then 0.5
            - If total installs are in between 500 - 1,000 then 1.0
            - If total installs are in between 1,000 - 5,000 then 1.5
            - If total installs are in between 5,000 - 10,000 then 2.0
            - If total installs are in between 10,000 - 50,000 then 2.5
    """
    def __init__(self, url):
        self.url = url
        self.soup = self._get_soup(self.url)

        self.app_rating = None
        self.app_updated = None
        self.app_installs = None

        # Score
        self.reputation_score = 0.0
        self.contribution_score = 0.0
        self.activity_score = 0.0
        self.total_score = 0.0

    def _get_soup(self, url):
        """
        Get HTML contents from the given website URL.
        """
        try:
            response = urlopen(url).read()
        except (HTTPError, URLError, TypeError):
            print("App Details not Found")
            return
        soup = BeautifulSoup(response, 'html5lib')
        return soup

    def _diff_month(self, d1, d2):
        """
        Returns month difference between two dates
        """
        return (d1.year - d2.year)*12 + d1.month - d2.month

    def _apply_app_rating_algorithm(self):
        """
        Apply rating algorithm based on scraped data
        """
        self.get_reputation_score()  # App Rating
        self.get_contribution_score()  # App Installs
        self.get_activity_score()  # App Updated
        self.total_score = (
            (self.reputation_score + self.activity_score + self.contribution_score) / 10
        )

    def get_app_rating(self):
        self.reputation_score = 0.0
        try:
            if self.soup is not None:
                self.reputation_score = float(
                    self.soup.find_all('div', class_='score')[0].text)
        except IndexError:
            self.reputation_score = 0.0

    def get_app_installs(self):
        self.app_installs = 0
        try:
            if self.soup is not None:
                app_installs = self.soup.findAll(attrs={'itemprop': 'numDownloads'})[0].text
                app_installs = app_installs.split("-")[0].strip()
                self.app_installs = int(app_installs.replace(",", ""))
        except IndexError:
            self.app_installs = 0

    def get_app_updated(self):
        try:
            if self.soup is not None:
                app_updated = self.soup.findAll(attrs={'itemprop': 'datePublished'})[0].text
                self.app_updated = datetime.strptime(app_updated, '%d %B %Y')
        except ValueError as e:
            print(e)
            self.app_updated = datetime.strptime(app_updated, '%B %d, %Y')
        except Exception as e:
            print(e)
            return

    def get_reputation_score(self):
        """
        App rating score
        """
        self.get_app_rating()
        return self.reputation_score / 10

    def get_contribution_score(self):
        """
        App installs score
        """
        self.get_app_installs()
        installs_index = {
            '100': 0.5, '500': 1.0, '1000': 1.5, '5000': 2.0, '10000': 2.5,
        }
        self.contribution_score = installs_index.get(str(self.app_installs))
        if self.app_installs > 10000:
            self.contribution_score = 2.5
        elif self.app_installs < 100:
            self.contribution_score = 0.0
        return self.contribution_score / 10

    def get_activity_score(self):
        """
        App updated score
        """
        self.get_app_updated()
        APP_UPDATE_THRESHOLD = 3  # In months
        updated_date_index = {
            "below": 2.5, "above": 1.2,
        }
        updated_date_score = 1.5
        if self.app_updated:
            if self._diff_month(datetime.now().date(), self.app_updated) <= APP_UPDATE_THRESHOLD:
                updated_date_score = updated_date_index['below']
            self.activity_score = updated_date_score
        return self.activity_score / 10

    def get_total_score(self):
        self._apply_app_rating_algorithm()
        return float("{0:.2f}".format(self.total_score))
