from base64 import urlsafe_b64encode, urlsafe_b64decode
from ariadne import ScalarType

_B64_SCALAR = ScalarType('B64')


@_B64_SCALAR.serializer
def r_b64_scalar(val, *_):
    # if bytes are received return b64
    if isinstance(val, bytes):
        return urlsafe_b64encode(val).decode()
    return val


@_B64_SCALAR.value_parser
def r_b64_value(val):
    return urlsafe_b64decode(val)


@_B64_SCALAR.literal_parser
def r_b64_literal(ast):
    value = bytes(ast.value, 'utf-8')
    return r_b64_value(value)


SCALAR = [
    _B64_SCALAR,
]
