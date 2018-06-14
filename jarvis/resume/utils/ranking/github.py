from jarvis.resume.utils.extractor import github_user_details
from .algorithm_base import AlgorithmAbstractClass
import datetime
import collections
import sys


class GithubEnum:
    """Enum Class contains all the constants that are used in the GitHub Algorithm.
    Changing the values of the constant will change the behaviour of the GitHub Algorithm."""
    # user types
    # This Algorithm is divided on the basis of six kinds of user.
    USER_NEW_ACTIVE = 0
    USER_NEW_INACTIVE = 1
    USER_MEDIUM_ACTIVE = 2
    USER_MEDIUM_INACTIVE = 3
    USER_OLD_ACTIVE = 4
    USER_OLD_INACTIVE = 5

    # User Activity
    # Checks whether the user is active or inactive based on account creation date, last commit date and
    # reputation change per month.
    USER_ACTIVITY_VARIABLES = collections.namedtuple(
        "USER_ACTIVITY", "months_passed_min months_passed_max days_passed_min days_passed_max"

    )

    USER_ACTIVITY_MAPPING = {
        USER_NEW_ACTIVE: USER_ACTIVITY_VARIABLES(0, 6, 0, 7),
        USER_NEW_INACTIVE: USER_ACTIVITY_VARIABLES(0, 6, 7, sys.maxsize),
        USER_MEDIUM_ACTIVE: USER_ACTIVITY_VARIABLES(7, 18, 0, 7),
        USER_MEDIUM_INACTIVE: USER_ACTIVITY_VARIABLES(7, 18, 7, sys.maxsize),
        USER_OLD_ACTIVE: USER_ACTIVITY_VARIABLES(19, sys.maxsize, 0, 7),
        USER_OLD_INACTIVE: USER_ACTIVITY_VARIABLES(19, sys.maxsize, 7, sys.maxsize)
    }

    # Activity Score
    # Score assigned on the basis of user activity
    USER_ACTIVE_SCORE = 0.2
    USER_INACTIVE_SCORE = 0.1

    USER_ACTIVE = [USER_NEW_ACTIVE, USER_MEDIUM_ACTIVE, USER_OLD_ACTIVE]
    USER_INACTIVE = [USER_NEW_INACTIVE, USER_MEDIUM_INACTIVE, USER_OLD_INACTIVE]

    # User Contribution
    # User Contributions calculated on the basis no. of repositories users have in their GitHub account.
    USER_CONTRIBUTION_RANGE_TYPE = collections.namedtuple(
        "USER_CONTRIBUTION_VARIABLES", "high low"
    )
    USER_CONTRIBUTION_MAPPING = {
        USER_CONTRIBUTION_RANGE_TYPE(sys.maxsize, 61): 0.6,
        USER_CONTRIBUTION_RANGE_TYPE(60, 51): 0.5,
        USER_CONTRIBUTION_RANGE_TYPE(50, 41): 0.4,
        USER_CONTRIBUTION_RANGE_TYPE(40, 31): 0.3,
        USER_CONTRIBUTION_RANGE_TYPE(30, 21): 0.2,
        USER_CONTRIBUTION_RANGE_TYPE(20, 11): 0.1,
        USER_CONTRIBUTION_RANGE_TYPE(10, 1): 0.05,
    }

    # User Reputation
    # Calculated on the basis on number of repositories
    USER_REPUTATION_RANGE_TYPE = collections.namedtuple(
        'USER_REPUTATION_VARIABLES', "high low"
    )
    # New User
    USER_NEW_REPUTATION_MAPPING = {
        USER_REPUTATION_RANGE_TYPE(sys.maxsize, 27): 0.2,
        USER_REPUTATION_RANGE_TYPE(27, 23): 0.16,
        USER_REPUTATION_RANGE_TYPE(23, 18): 0.12,
        USER_REPUTATION_RANGE_TYPE(18, 14): 0.08,
        USER_REPUTATION_RANGE_TYPE(13, 9): 0.04,
        USER_REPUTATION_RANGE_TYPE(8, 4): 0.02,
        USER_REPUTATION_RANGE_TYPE(3, 1): 0.01,

    }
    # Medium User
    USER_MEDIUM_REPUTATION_MAPPING = {
        USER_REPUTATION_RANGE_TYPE(sys.maxsize, 50): 0.2,
        USER_REPUTATION_RANGE_TYPE(49, 45): 0.16,
        USER_REPUTATION_RANGE_TYPE(44, 40): 0.12,
        USER_REPUTATION_RANGE_TYPE(40, 36): 0.08,
        USER_REPUTATION_RANGE_TYPE(35, 31): 0.04,
        USER_REPUTATION_RANGE_TYPE(31, 27): 0.02,
        USER_REPUTATION_RANGE_TYPE(26, 1): 0.01,

    }
    # Old User
    USER_OLD_REPUTATION_MAPPING = {
        USER_REPUTATION_RANGE_TYPE(sys.maxsize, 76): 0.2,
        USER_REPUTATION_RANGE_TYPE(75, 71): 0.16,
        USER_REPUTATION_RANGE_TYPE(70, 66): 0.12,
        USER_REPUTATION_RANGE_TYPE(65, 61): 0.08,
        USER_REPUTATION_RANGE_TYPE(60, 56): 0.04,
        USER_REPUTATION_RANGE_TYPE(55, 51): 0.02,
        USER_REPUTATION_RANGE_TYPE(50, 1): 0.01,

    }
    USER_REPUTATION_REMAINING_SCORE = 0.01  # if total no. of repos greater than 1


class GitHubScore(AlgorithmAbstractClass):
    """
    Calculates HitHub Score based on:
    1. No. of Followers a user Have.
    2. No. of Repositories.
    3. Activity of the User based on account creation date, last commit date and reputation change per month.
    """
    def __init__(self, user_name):
        self._user_name = user_name
        self.total_score = 0
        self.activity_score = 0
        self.contribution_score = 0
        self.reputation_score = 0
        self._user_details = {}

    def _extract(self):
        """
        Extracts Details of GitHub User using helper function.
        """
        if not self._user_details:
            self._user_details = github_user_details(self._user_name)
            today_date = datetime.date.today()
            account_creation_date = self._user_details['account_created_at'].date()
            account_updated_at = self._user_details['last_updated_at'].date()
            months_passed = (today_date - account_creation_date).days / float(30)
            days_passed = (today_date - account_updated_at).days
            self.user_type = self._type_of_user(months_passed, days_passed)
            self.total_no_of_repos = self._user_details['public_repos']
            self.contribution_score = self.get_contribution_score()
            self.no_of_followers = self._user_details['followers']
            # self._repo_details = self._user_details['repo_details']

    def _type_of_user(self, months_passed, days_passed):
        """
        Finding the type of user whether its new, medium, old
        :param months_passed, days_passed:int
        :return: int -  the returned value can be matched with the type of user in Enum Class
        """
        for key, value in list(GithubEnum.USER_ACTIVITY_MAPPING.items()):
            if key in GithubEnum.USER_ACTIVE:
                if ((value.months_passed_min <= months_passed <= value.months_passed_max) and
                        (value.days_passed_min <= days_passed <= value.days_passed_max)):
                    return key
            else:
                if ((value.months_passed_min <= months_passed <= value.months_passed_max) and
                        (value.days_passed_min <= days_passed)):
                    return key
        return "Unknown User"

    def get_activity_score(self):
        """
        Calculating activity score
        :return: float
        """
        self._extract()
        if self.user_type in GithubEnum.USER_ACTIVE:
            self.activity_score = GithubEnum.USER_ACTIVE_SCORE
        elif self.user_type in GithubEnum.USER_INACTIVE:
            self.activity_score = GithubEnum.USER_INACTIVE_SCORE
        return self.activity_score

    def get_contribution_score(self):
        """
        Calculating contribution score based on number of repositories.
        :return: float
        """
        self._extract()
        for key in GithubEnum.USER_CONTRIBUTION_MAPPING:
            if key.high >= self.total_no_of_repos >= key.low:
                return GithubEnum.USER_CONTRIBUTION_MAPPING[key]
        return 0

    def get_github_user_details(self):
        return self._user_details

    def get_reputation_score(self):
        """
        Calculating reputation score based on number of followers.
        :return: float
        """
        self._extract()
        if self.user_type == 0 or self.user_type == 1:
            for key in GithubEnum.USER_NEW_REPUTATION_MAPPING:
                if key.high >= self.no_of_followers >= key.low:
                    return GithubEnum.USER_NEW_REPUTATION_MAPPING[key]
        elif self.user_type == 2 or self.user_type == 3:
            for key in GithubEnum.USER_MEDIUM_REPUTATION_MAPPING:
                if key.high >= self.no_of_followers >= key.low:
                    return GithubEnum.USER_MEDIUM_REPUTATION_MAPPING[key]
        elif self.user_type == 4 or self.user_type == 5:
            for key in GithubEnum.USER_OLD_REPUTATION_MAPPING:
                if key.high >= self.no_of_followers >= key.low:
                    return GithubEnum.USER_OLD_REPUTATION_MAPPING[key]
        return 0

    def get_total_score(self, git_reputation_score, git_contribution_score, git_activity_score):
        total_score = git_activity_score + git_contribution_score + git_reputation_score
        return total_score

    # # currently not used.
    # def _get_repos_average_points(self):
    #     self._get_details()
    #     for repo in self._repo_details.values():
    #         if not repo['is_forked']:
    #             self._repo_stars = repo['no_of_stars']
    #             self._repo_forks = repo['no_of_forks']
    #             self._repo_creation_date = repo['repo_created_at']
    #             self._days_elapsed_since_creation = (self._today_date - self._repo_creation_date).days
    #             self.repo_points = abs(self._repo_stars + self._repo_forks - 1)/pow(float(self._days_elapsed_since_creation), 0.5)
    #             self.total_repo_points += self.repo_points
    #     if self._total_no_repos == 0:
    #         self.average_repo_points = 0
    #     else:
    #         self.average_repo_points = self.total_repo_points / self._total_no_repos
    #     return self.average_repo_points

    # currently not used
    # def _get_final_repo_score(self):
    #     # total repo score = 0.6
    #     self._get_repos_average_points()
    #     if self.average_repo_points >= 15:
    #         self.total_repo_score += 0.6
    #     elif 15 > self.average_repo_points >= 12:
    #         self.total_repo_score += 0.5
    #     elif 12 > self.average_repo_points >= 9:
    #         self.total_repo_score += 0.4
    #     elif 9 > self.average_repo_points >= 6:
    #         self.total_repo_score += 0.3
    #     elif 6 > self.average_repo_points >= 3:
    #         self.total_repo_score += 0.2
    #     elif 3 > self.average_repo_points >= 1:
    #         self.total_repo_score += 0.1
    #     elif 1 > self.average_repo_points > 0:
    #         self.total_repo_score += 0.05
    #     return self.total_repo_score

