from ariadne import QueryType

QUERY = QueryType()


@QUERY.field("API")
def r_api(*_):
    return "FeatherLight"
