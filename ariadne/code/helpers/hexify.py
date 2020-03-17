"""function for recusively hex encoding bytes values in a json-like-dict"""
from code.helpers.mixins import LoggerMixin
import copy

temp = LoggerMixin()

#helper function for determining if nest value is valid
def _valid_type(i):
    return isinstance(i, dict) or isinstance(i, list)

#helper function for making value hex or leaving it the same
def _make_hex(i):
    return i.hex() if isinstance(i, bytes) else copy.copy(i)


def hexify(iterable):
    if isinstance(iterable, dict):
        new = {}
        for key, value in iterable.items():
            if _valid_type(value):
                new[key] = hexify(value)
            new[key] = _make_hex(value)
            if key == 'payment_addr':
                temp.logger.critical(f"set {key} to {new[key]}")
        return new

    elif isinstance(iterable, list):
        new = []
        for item in iterable:
            if _valid_type(item):
                new.append(hexify(item))
            new.append(_make_hex(item))
        return new

    else:
        raise ValueError(f"Invalid iterable: {iterable} passed")