import os
from ariadne import QueryType

QUERY = QueryType()


@QUERY.field("network")
def r_network(*_):
    return os.environ.get("NETWORK").upper()
