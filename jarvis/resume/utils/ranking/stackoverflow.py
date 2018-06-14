# StackOverflow score
from jarvis.resume.utils.extractor import stackoverflow_user_details
import datetime
from .algorithm_base import AlgorithmAbstractClass
import collections
import sys


class StackOverflowEnum:
    """Enum Class contains all the constants that are used in the StackOverflow Algorithm.
    Changing the values of the constant will change the behaviour of the StackOverflow Algorithm."""

    # user types
    USER_NEW_ACTIVE = 0
    USER_NEW_INACTIVE = 1
    USER_MEDIUM_ACTIVE = 2
    USER_MEDIUM_INACTIVE = 3
    USER_OLD_ACTIVE = 4
    USER_OLD_INACTIVE = 5

    # User Types independent of activity
    USER_NEW = 0
    USER_MEDIUM = 1
    USER_OLD = 2

    # Badge types
    BADGE_GOLD = 0
    BADGE_SILVER = 1
    BADGE_BRONZE = 2

    # User Activity
    USER_ACTIVITY_VARIABLES = collections.namedtuple(
        "USER_ACTIVITY", "months_passed_min months_passed_max days_passed_min days_passed_max"
                         " reputation_change_month_min reputation_change_month_max"
    )

    USER_ACTIVITY_MAPPING = {
        USER_NEW_ACTIVE: USER_ACTIVITY_VARIABLES(0, 4, 0, 7, 10, sys.maxsize),
        USER_NEW_INACTIVE: USER_ACTIVITY_VARIABLES(0, 4, 0, 7, 0, 0),
        USER_MEDIUM_ACTIVE: USER_ACTIVITY_VARIABLES(4, 24, 0, 7, 40, sys.maxsize),
        USER_MEDIUM_INACTIVE: USER_ACTIVITY_VARIABLES(4, 24, 0, 7, 0, 0),
        USER_OLD_ACTIVE: USER_ACTIVITY_VARIABLES(25, sys.maxsize, 0, 7, 70, sys.maxsize),
        USER_OLD_INACTIVE: USER_ACTIVITY_VARIABLES(25, sys.maxsize, 0, 7, 0, 0)
    }

    # Activity Score
    USER_ACTIVE_SCORE = 0.2
    USER_INACTIVE_SCORE = 0.1

    USER_ACTIVE = [USER_NEW_ACTIVE, USER_MEDIUM_ACTIVE, USER_OLD_ACTIVE]
    USER_INACTIVE = [USER_NEW_INACTIVE, USER_MEDIUM_INACTIVE, USER_OLD_INACTIVE]

    # Contribution Score
    # Answer Score
    ANSWER_SCORE_RANGE_TYPE = collections.namedtuple("ANSWER_SCORE_RANGE_TYPE", "low high")
    ANSWER_SCORE_MAPPING = {
        ANSWER_SCORE_RANGE_TYPE(0, 25): 0.1,
        ANSWER_SCORE_RANGE_TYPE(26, 50): 0.07,
        ANSWER_SCORE_RANGE_TYPE(51, 70): 0.04,
    }

    # Acceptance Score
    ACCEPTANCE_SCORE_RANGE_TYPE = collections.namedtuple("ACCEPTANCE_SCORE_RANGE_TYPE", "low high")
    ACCEPTANCE_SCORE_MAPPING = {
        ACCEPTANCE_SCORE_RANGE_TYPE(0, 25): 0.1,
        ACCEPTANCE_SCORE_RANGE_TYPE(26, 50): 0.07,
        ACCEPTANCE_SCORE_RANGE_TYPE(51, 70): 0.04,
    }

    # User Reputation

    USER_REPUTATION_RANGE_TYPE = collections.namedtuple(
        'USER_REPUTATION_VARIABLES', "high low"
    )
    # New User
    USER_NEW_REPUTATION_MAPPING = {
        USER_REPUTATION_RANGE_TYPE(sys.maxsize, 151): 0.3,
        USER_REPUTATION_RANGE_TYPE(150, 121): 0.24,
        USER_REPUTATION_RANGE_TYPE(120, 91): 0.18,
        USER_REPUTATION_RANGE_TYPE(90, 61): 0.12,
        USER_REPUTATION_RANGE_TYPE(60, 31): 0.06,
        # else 0.03
    }
    # Medium User
    USER_MEDIUM_REPUTATION_MAPPING = {
        USER_REPUTATION_RANGE_TYPE(sys.maxsize, 1201): 0.3,
        USER_REPUTATION_RANGE_TYPE(1200, 1001): 0.24,
        USER_REPUTATION_RANGE_TYPE(1000, 801): 0.18,
        USER_REPUTATION_RANGE_TYPE(800, 601): 0.12,
        USER_REPUTATION_RANGE_TYPE(600, 401): 0.06,
        # else 0.03
    }
    # Old User
    USER_OLD_REPUTATION_MAPPING = {
        USER_REPUTATION_RANGE_TYPE(sys.maxsize, 3001): 0.3,
        USER_REPUTATION_RANGE_TYPE(3000, 2601): 0.24,
        USER_REPUTATION_RANGE_TYPE(2600, 2201): 0.18,
        USER_REPUTATION_RANGE_TYPE(2200, 1801): 0.12,
        USER_REPUTATION_RANGE_TYPE(1800, 1401): 0.06,
        # else 0.03
    }
    USER_REPUTATION_REMAINING_SCORE = 0.03

    # User Badges
    USER_BADGES_RANGE_TYPE = collections.namedtuple(
        'USER_BADGES_RANGE_TYPE', "high low"
    )
    USER_BADGES_MAPPING = {
        USER_NEW_ACTIVE: {
            BADGE_GOLD: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 0): 0.3
            },
            BADGE_SILVER: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 0): 0.26
            },
            BADGE_BRONZE: {
                USER_BADGES_RANGE_TYPE(5, 1): 0.06,
                USER_BADGES_RANGE_TYPE(10, 6): 0.1,
                USER_BADGES_RANGE_TYPE(15, 11): 0.14,
                USER_BADGES_RANGE_TYPE(20, 16): 0.18,
                USER_BADGES_RANGE_TYPE(25, 21): 0.22,
            }
        },
        USER_MEDIUM_ACTIVE: {
            BADGE_GOLD: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 3): 0.3,
                USER_BADGES_RANGE_TYPE(3, 1): 0.25

            },
            BADGE_SILVER: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 15): 0.3,
                USER_BADGES_RANGE_TYPE(14, 9): 0.25,
                USER_BADGES_RANGE_TYPE(9, 4): 0.2,
                USER_BADGES_RANGE_TYPE(3, 1): 0.05,

            },
            BADGE_BRONZE: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 41): 0.3,
                USER_BADGES_RANGE_TYPE(40, 36): 0.25,
                USER_BADGES_RANGE_TYPE(36, 32): 0.2,
                USER_BADGES_RANGE_TYPE(31, 27): 0.15,
                USER_BADGES_RANGE_TYPE(26, 22): 0.1,
                USER_BADGES_RANGE_TYPE(21, 1): 0.05,
            }
        },
        USER_OLD_ACTIVE: {
            BADGE_GOLD: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 8): 0.3,
                USER_BADGES_RANGE_TYPE(7, 3): 0.25

            },
            BADGE_SILVER: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 26): 0.3,
                USER_BADGES_RANGE_TYPE(25, 21): 0.25,
                USER_BADGES_RANGE_TYPE(20, 16): 0.2,
                USER_BADGES_RANGE_TYPE(15, 0): 0.025,

            },
            BADGE_BRONZE: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 67): 0.3,
                USER_BADGES_RANGE_TYPE(66, 62): 0.25,
                USER_BADGES_RANGE_TYPE(61, 57): 0.2,
                USER_BADGES_RANGE_TYPE(56, 52): 0.15,
                USER_BADGES_RANGE_TYPE(51, 47): 0.1,
                USER_BADGES_RANGE_TYPE(46, 42): 0.05,
                USER_BADGES_RANGE_TYPE(41, 1): 0.025,
            },
        },
        USER_NEW_INACTIVE: {
            BADGE_GOLD: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 0): 0.3
            },
            BADGE_SILVER: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 0): 0.26
            },
            BADGE_BRONZE: {
                USER_BADGES_RANGE_TYPE(5, 1): 0.06,
                USER_BADGES_RANGE_TYPE(10, 6): 0.1,
                USER_BADGES_RANGE_TYPE(15, 11): 0.14,
                USER_BADGES_RANGE_TYPE(20, 16): 0.18,
                USER_BADGES_RANGE_TYPE(25, 21): 0.22,
            }
        },
        USER_MEDIUM_INACTIVE: {
            BADGE_GOLD: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 3): 0.3,
                USER_BADGES_RANGE_TYPE(3, 1): 0.25

            },
            BADGE_SILVER: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 15): 0.3,
                USER_BADGES_RANGE_TYPE(14, 9): 0.25,
                USER_BADGES_RANGE_TYPE(9, 4): 0.2,
                USER_BADGES_RANGE_TYPE(3, 1): 0.05,

            },
            BADGE_BRONZE: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 41): 0.3,
                USER_BADGES_RANGE_TYPE(40, 36): 0.25,
                USER_BADGES_RANGE_TYPE(36, 32): 0.2,
                USER_BADGES_RANGE_TYPE(31, 27): 0.15,
                USER_BADGES_RANGE_TYPE(26, 22): 0.1,
                USER_BADGES_RANGE_TYPE(21, 1): 0.05,
            }
        },
        USER_OLD_INACTIVE: {
            BADGE_GOLD: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 8): 0.3,
                USER_BADGES_RANGE_TYPE(7, 3): 0.25

            },
            BADGE_SILVER: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 26): 0.3,
                USER_BADGES_RANGE_TYPE(25, 21): 0.25,
                USER_BADGES_RANGE_TYPE(20, 16): 0.2,
                USER_BADGES_RANGE_TYPE(15, 0): 0.025,

            },
            BADGE_BRONZE: {
                USER_BADGES_RANGE_TYPE(sys.maxsize, 67): 0.3,
                USER_BADGES_RANGE_TYPE(66, 62): 0.25,
                USER_BADGES_RANGE_TYPE(61, 57): 0.2,
                USER_BADGES_RANGE_TYPE(56, 52): 0.15,
                USER_BADGES_RANGE_TYPE(51, 47): 0.1,
                USER_BADGES_RANGE_TYPE(46, 42): 0.05,
                USER_BADGES_RANGE_TYPE(41, 1): 0.025,
            },
        }
    }


class StackOverflowScore(AlgorithmAbstractClass):
    """
    Algorithm to calculate StackOverflow Rating.
    """

    def __init__(self, user_id):
        self._user_id = user_id
        self._user_details = {}
        self.activity_score = 0
        self.answer_score = 0
        self.reputation_score = 0

    def _extract(self):
        """Extracting Stackoverflow user details"""
        if not self._user_details:
            self._user_details = stackoverflow_user_details(self._user_id)
            today_date = datetime.date.today()
            months_passed = (today_date - self._user_details['account_creation_date'].date()).days / float(30)
            days_passed = (today_date - self._user_details['last_access_date'].date()).days
            reputation_change_per_month = self._user_details['reputation_change_month']
            self.user_type = self._type_of_user(months_passed=months_passed, days_passed=days_passed,
                                                reputation_change_per_month=reputation_change_per_month)
            total_no_of_questions = self._user_details['total_no_questions']
            total_no_of_unaccepted_questions = self._user_details['total_unaccepted_questions']
            total_no_of_unanswered_questions = self._user_details['total_unanswered_questions']
            self.answer_score = self._answer_score(total_no_of_questions=total_no_of_questions,
                                                   total_no_of_unanswered_questions=total_no_of_unanswered_questions)
            self.acceptance_score = self._acceptance_score(total_no_of_questions=total_no_of_questions,
                                                           total_no_of_unaccepted_questions=total_no_of_unaccepted_questions)
            total_reputation = self._user_details['reputation']
            self.user_followers_score = self._user_reputation_score(total_reputation, self.user_type)
            gold_badges = self._user_details['gold_badges_count']
            silver_badges = self._user_details['silver_badges_count']
            bronze_badges = self._user_details['bronze_badges_count']
            self.user_badges_score = self._user_badges_score(gold_badges, silver_badges, bronze_badges, self.user_type)
            self.reputation_score = self.user_badges_score + self.user_followers_score

    def _type_of_user(self, months_passed, days_passed, reputation_change_per_month):
        """Returns the type of user like new active, new inactive, medium active, medium inactive...."""
        for key, value in list(StackOverflowEnum.USER_ACTIVITY_MAPPING.items()):
            if key in StackOverflowEnum.USER_ACTIVE:
                if ((value.months_passed_min <= months_passed <= value.months_passed_max) and
                        (value.days_passed_min <= days_passed <= value.days_passed_max) and
                        (value.reputation_change_month_min <= reputation_change_per_month)):
                    return key
            else:
                if ((value.months_passed_min <= months_passed <= value.months_passed_max) and
                        (value.days_passed_min <= days_passed and
                            (value.reputation_change_month_min <= reputation_change_per_month or
                                reputation_change_per_month < value.reputation_change_month_min))):
                    return key
        return "Unknown User"

    def _answer_score(self, total_no_of_questions, total_no_of_unanswered_questions):
        """Calculates the answer rate."""
        if total_no_of_questions != 0:
            self._answer_rate = (total_no_of_unanswered_questions/float(total_no_of_questions)) * 100
            for key in StackOverflowEnum.ANSWER_SCORE_MAPPING:
                if key.low < self._answer_rate < key.high:
                    return StackOverflowEnum.ANSWER_SCORE_MAPPING[key]
        else:
            return 0

    def _acceptance_score(self, total_no_of_questions, total_no_of_unaccepted_questions):
        """Calculates the acceptance rate."""
        if total_no_of_questions != 0:
            self._acceptance_rate = (total_no_of_unaccepted_questions/float(total_no_of_questions)) * 100

            for key in StackOverflowEnum.ACCEPTANCE_SCORE_MAPPING:
                if key.low < self._answer_rate < key.high:
                    return StackOverflowEnum.ACCEPTANCE_SCORE_MAPPING[key]
        else:
            return 0

    def _user_reputation_score(self, total_reputation, user_type):
        """Calculates reputations score for a user based on total reputation."""
        if user_type == 0 or user_type == 1:
            for key in StackOverflowEnum.USER_NEW_REPUTATION_MAPPING:
                if key.high > total_reputation >= key.low:
                    return StackOverflowEnum.USER_NEW_REPUTATION_MAPPING[key]
        elif user_type == 2 or user_type == 3:
            for key in StackOverflowEnum.USER_MEDIUM_REPUTATION_MAPPING:
                if key.high > total_reputation >= key.low:
                    return StackOverflowEnum.USER_MEDIUM_REPUTATION_MAPPING[key]
        elif user_type == 4 or user_type == 5:
            for key in StackOverflowEnum.USER_OLD_REPUTATION_MAPPING:
                if key.high > total_reputation >= key.low:
                    return StackOverflowEnum.USER_OLD_REPUTATION_MAPPING[key]
        return StackOverflowEnum.USER_REPUTATION_REMAINING_SCORE

    def _user_badges_score(self, gold_badges, silver_badges, bronze_badges, user_type):
        """Calculates the badges score depends on gold, silver and bronze badges."""
        if user_type in list(StackOverflowEnum.USER_BADGES_MAPPING.keys()):
            for key, value in list(StackOverflowEnum.USER_BADGES_MAPPING.items()):
                for k, v in list(value.items()):
                    for item in v:
                        if item.low <= gold_badges <= item.high:
                            return v[item]
                        elif item.low <= silver_badges <= item.high:
                            return v[item]
                        elif item.low <= bronze_badges <= item.high:
                            return v[item]
                return 0
            return 0

    def get_stackoverflow_user_details(self):
        return self._user_details

    def get_activity_score(self):
        """Calculates the total activity score for a user."""
        # total score = 0.2
        self._extract()
        if self.user_type in StackOverflowEnum.USER_ACTIVE:
            self.activity_score = StackOverflowEnum.USER_ACTIVE_SCORE
        elif self.user_type in StackOverflowEnum.USER_INACTIVE:
            self.activity_score = StackOverflowEnum.USER_INACTIVE_SCORE
        return self.activity_score

    def get_contribution_score(self):
        """Calculates the total contribution score based on number of followers"""
        self._extract()
        if not self.acceptance_score and not self.answer_score:
            return float(0.0)
        return self.acceptance_score + self.answer_score

    def get_reputation_score(self):
        """Calculates the total reputation score, sum of badges score and user reputation score"""
        self._extract()
        return self.reputation_score

    def get_total_score(self):
        """Returns the total score obtained."""
        return float(
            "{0:.2f}".format(self.get_activity_score() + self.get_contribution_score() + self.get_reputation_score()))


