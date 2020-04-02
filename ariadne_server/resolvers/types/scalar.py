import codecs
from ariadne import ScalarType

_B64_SCALAR = ScalarType('B64')


@_B64_SCALAR.serializer
def r_b64_scalar(val, *_):
    # if bytes are received return hex
    if isinstance(val, bytes):
        return codecs.encode(val, 'base-64').decode()


@_B64_SCALAR.value_parser
def r_b64_value(val):
    return codecs.decode(val, 'base-64')


@_B64_SCALAR.literal_parser
def r_b64_literal(ast):
    value = bytes(ast.value, 'utf-8')
    return r_b64_value(value)


SCALAR = [
    _B64_SCALAR,
]
