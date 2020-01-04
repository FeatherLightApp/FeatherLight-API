"""module for defining helpful mixins"""
import logging

class LoggerMixin(object):
    @property
    def logger(self):
        name = '.'.join([
            self.__module__,
            self.__class__.__name__
        ])
        return logging.getLogger(name)


class DotDict(dict):
    """access dictionary with dot notaion"""
    __getattr__ = super().get
    __setattr__ = super().__setitem__
    __delattr__ = super().__delitem__