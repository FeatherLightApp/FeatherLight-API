import abc
from code.helpers.mixins import LoggerMixin

class AbstractMethod(LoggerMixin, metaclass=abc.ABCMeta):

    # @abc.abstractmethod
    # async def get_params(self):
    #     pass

    @abc.abstractmethod
    async def run(self):
        pass
