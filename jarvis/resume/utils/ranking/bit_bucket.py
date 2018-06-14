from jarvis.resume.utils.extractor import bit_bucket_user_details
import datetime
from .algorithm_base import AlgorithmAbstractClass
import sys
import collections


class BitBucketEnum:
    """
    Enum Class contains all the constants that are used in the Bit Bucket Algorithm.
    Changing the values of the constant will change the behaviour of the BitBucket Algorithm.
    """
    # types of users
    # BitBucket Algorithm is divided on the basis of these three kinds of user.
    USER_NEW_ACTIVE = 0
    USER_MEDIUM_ACTIVE = 1
    USER_OLD_ACTIVE = 2

    # User Activity
    # Checks whether the user is active or inactive
    USER_ACTIVITY_VARIABLES = collections.namedtuple(
        "USER_ACTIVITY", "months_passed_min months_passed_max"
    )

    USER_ACTIVITY_MAPPING = {
        USER_NEW_ACTIVE: USER_ACTIVITY_VARIABLES(0, 6),
        USER_MEDIUM_ACTIVE: USER_ACTIVITY_VARIABLES(7, 18),
        USER_OLD_ACTIVE: USER_ACTIVITY_VARIABLES(19, sys.maxsize),

    }

    # Activity Score
    # Score assigned on the basis of user activity
    USER_ACTIVE_SCORE = 0.2
    USER_INACTIVE_SCORE = 0.1

    USER_TYPES = [USER_NEW_ACTIVE, USER_MEDIUM_ACTIVE, USER_OLD_ACTIVE]

    # User Contribution
    # User Contributions calculated on the basis no. of repositories users have in their bitbucket account.
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
    # Calculated on the basis of no. of followers
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


class BitBucketScore(AlgorithmAbstractClass):
    """
    Calculates BitBucket Score based on:
    1. No. of Followers a user Have.
    2. No. of Repositories.
    3. Activity of the User based on account creation date.
    """
    # total score = 1
    # 0.6 + 0.2 + 0.2
    def __init__(self, user_name):
        self._user_name = user_name
        self.total_score = 0
        self.activity_score = 0
        self.contribution_score = 0
        self.reputation_score = 0
        self._user_details = {}

    def _extract(self):
        if not self._user_details:
            self._user_details = bit_bucket_user_details(self._user_name)
            today_date = datetime.date.today()
            account_created_at = self._user_details['account_created_at']
            months_passed = (today_date - account_created_at.date()).days/float(30)
            self.total_no_of_repos = self._user_details['total_no_of_repos']
            self.no_of_followers = self._user_details['followers']
            self.user_type = self._type_of_user(months_passed)

    def get_bit_bucket_user_details(self):
        return self._user_details

    def get_contribution_score(self):
        """
        Calculating contribution score based on number of repos
        :return: float
        """
        self._extract()
        for key in BitBucketEnum.USER_CONTRIBUTION_MAPPING:
            if key.high >= self.total_no_of_repos >= key.low:
                return BitBucketEnum.USER_CONTRIBUTION_MAPPING[key]
        return 0

    def get_reputation_score(self):
        """
        Calculating reputation score based on number of followers.
        :return: float
        """
        self._extract()
        if self.user_type == 0:
            for key in BitBucketEnum.USER_NEW_REPUTATION_MAPPING:
                if key.high >= self.no_of_followers >= key.low:
                    return BitBucketEnum.USER_NEW_REPUTATION_MAPPING[key]
        elif self.user_type == 1:
            for key in BitBucketEnum.USER_MEDIUM_REPUTATION_MAPPING:
                if key.high >= self.no_of_followers >= key.low:
                    return BitBucketEnum.USER_MEDIUM_REPUTATION_MAPPING[key]
        elif self.user_type == 2:
            for key in BitBucketEnum.USER_OLD_REPUTATION_MAPPING:
                if key.high >= self.no_of_followers >= key.low:
                    return BitBucketEnum.USER_OLD_REPUTATION_MAPPING[key]
        return 0

    def _type_of_user(self, months_passed):
        """
        Finding the type of user whether its new, medium, old
        :param months_passed:int
        :return: int -  the returned value can be matched with the type of user in Enum Class
        """
        for key, value in list(BitBucketEnum.USER_ACTIVITY_MAPPING.items()):
            if key in BitBucketEnum.USER_TYPES:
                if value.months_passed_min <= months_passed <= value.months_passed_max:
                    return key
            else:
                return "Inactive User"
        return "Unknown User"

    def get_activity_score(self):
        """
        Calculating activity score
        :return: float
        """
        self._extract()
        if self.user_type in BitBucketEnum.USER_TYPES:
            return BitBucketEnum.USER_ACTIVE_SCORE
        else:
            return BitBucketEnum.USER_INACTIVE_SCORE

    def get_total_score(self, bit_activity_score, bit_contribution_score, bit_reputation_score):
        total_score = bit_activity_score + bit_contribution_score + bit_reputation_score
        return total_score



