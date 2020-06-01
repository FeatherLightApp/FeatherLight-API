from ariadne import QueryType

QUERY = QueryType()


@QUERY.field("version")
def r_version(*_):
    return "1.0"
