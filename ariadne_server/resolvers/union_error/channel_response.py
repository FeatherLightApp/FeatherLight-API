from ariadne import UnionType
from classes.error import Error

CHANNEL_RESPONSE = Union('ChannelResponse')

@CHANNEL_RESPONSE.type_resolver
def r_channel_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    return 'ChannelPayload'