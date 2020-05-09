"""import and define schem execution"""
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers
)
from .query import QUERY
from .mutation import MUTATION
from .subscription import SUBSCRIPTION
from .objects import OBJECTS
from .union_error import UNION_ERROR
from .union import UNION
from .directives import AuthDirective, RatelimitDirective

_TYPE_DEFS = load_schema_from_path('schema')

SCHEMA = make_executable_schema(
    _TYPE_DEFS,
    [
        *QUERY,
        *MUTATION,
        *SUBSCRIPTION,
        *OBJECTS,
        *UNION_ERROR,
        *UNION,
    ],
    snake_case_fallback_resolvers,
    directives={
        'auth': AuthDirective,
        'limit': RatelimitDirective
    }
)
