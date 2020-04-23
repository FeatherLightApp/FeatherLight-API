from ariadne import UnionType
from models.invoice import Invoice
from pymacaroons import Macaroon

FEED_ITEM = UnionType('FeedItem')

@FEED_ITEM.type_resolver
def r_feed_item(obj, info, *_):
    m = Macaroon.deserialize(info.context['request'].headers['Authorization'].replace('Bearer ', ''))
    if isinstance(obj, Invoice):
        if m.identifier == obj.payee:
            return 'UserInvoice'
        if m.identifier == obj.payer:
            return 'PaidInvoice'
    return 'Deposit'
