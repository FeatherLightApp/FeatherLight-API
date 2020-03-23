"""module for abstract api methods"""
import abc
from ...helpers.mixins import LoggerMixin
from .user_api import User

class AbstractMethod(LoggerMixin, metaclass=abc.ABCMeta):

    # @abc.abstractmethod
    # async def get_params(self):
    #     pass

    @abc.abstractmethod
    async def run(self, user: User):
        """abstract method for defining api methods"""
