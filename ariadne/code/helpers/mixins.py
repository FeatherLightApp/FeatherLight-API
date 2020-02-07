"""module for defining helpful mixins"""
import logging

class LoggerMixin(object):
    """Mixin for adding logger to a class"""
    @property
    def logger(self):
        name = '.'.join([
            self.__module__,
            self.__class__.__name__
        ])
        return logging.getLogger(name)


class DotDict(dict):
    """access dictionary with dot notaion"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__