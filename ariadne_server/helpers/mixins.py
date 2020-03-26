"""module for defining helpful mixins"""
import logging


class LoggerMixin:
    """Mixin for adding logger to a class"""
    @property
    def logger(self):
        name = '.'.join([
            self.__module__,
            self.__class__.__name__
        ])
        root = logging.getLogger()
        root.handlers.clear()
        logger = logging.getLogger(name)

        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)-15s %(name)-12s: %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger


class DotDict(dict):
    """access dictionary with dot notaion"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
