from ariadne import QueryType
from classes import User

QUERY = QueryType()


@QUERY.field("nodeBalance")
@QUERY.field("me")
@QUERY.field("channels")
def r_passthrough(user: User, *_):
    return user
