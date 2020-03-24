from ariadne import ScalarType

_HEX_SCALAR = ScalarType('Hex')

@_HEX_SCALAR.serializer
def r_hex_scalar(val):
    #if bytes are received return hex
    if isinstance(val, bytes):
        return val.hex()
    # if value is already hex return value
    if int(val, 16):
        return val

_DATETIME_SCALAR = ScalarType('Datetime')

SCALAR = [
    _HEX_SCALAR,
    _DATETIME_SCALAR
]