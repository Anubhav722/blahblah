from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class AlgorithmAbstractClass():
    """
    Abstract Base Class for all the algorithms
    """
    @abstractmethod
    def get_activity_score(self):
        pass

    @abstractmethod
    def get_reputation_score(self):
        pass

    @abstractmethod
    def get_contribution_score(self):
        pass

    @abstractmethod
    def get_total_score(self):
        pass

