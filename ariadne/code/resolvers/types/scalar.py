from datetime import datetime
from ariadne import ScalarType

HEX_SCALAR = ScalarType('Hex')

@HEX_SCALAR.serializer
def r_hex_scalar(val):
    #if bytes are received return hex
    if type(val) is bytes:
        return val.hex()
    # if value is already hex return value
    if int(val, 16):
        return val

DATETIME_SCALAR = ScalarType('Datetime')
