"""import and define schem execution"""
import os
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
)
from .query import QUERY
from .mutation import MUTATION
from .subscription import SUBSCRIPTION
from .objects import OBJECTS
from .union_error import UNION_ERROR
from .union import UNION
from .scalar import SCALAR
from .directives import AuthDirective, RatelimitDirective

schema_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'schema'))
_TYPE_DEFS = load_schema_from_path(schema_dir)

SCHEMA = make_executable_schema(
    _TYPE_DEFS,
    [*QUERY, *MUTATION, *SUBSCRIPTION, *OBJECTS, *UNION_ERROR, *UNION, *SCALAR],
    snake_case_fallback_resolvers,
    directives={"auth": AuthDirective, "limit": RatelimitDirective},
)
