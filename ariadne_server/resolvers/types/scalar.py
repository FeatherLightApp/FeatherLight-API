from ariadne import ScalarType

_HEX_SCALAR = ScalarType('Hex')


@_HEX_SCALAR.serializer
def r_hex_scalar(val, *_):
    # if bytes are received return hex
    if isinstance(val, bytes):
        return val.hex()
    # if value is already hex return value
    if int(val, 16):
        return val


@_HEX_SCALAR.value_parser
def r_hex_value(val):
    return bytes.fromhex(val)


@_HEX_SCALAR.literal_parser
def r_hex_literal(ast):
    value = str(ast.value)
    return r_hex_value(value)


SCALAR = [
    _HEX_SCALAR,
]
