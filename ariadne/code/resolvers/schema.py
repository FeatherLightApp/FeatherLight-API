"""import and define schem execution"""
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers
)
from .types import TYPES as resolvers
from .directives import AuthDirective

TYPE_DEFS = load_schema_from_path('code/schema/')

SCHEMA = make_executable_schema(
    TYPE_DEFS,
    resolvers,
    snake_case_fallback_resolvers,
    directives={
        'auth': AuthDirective
    }
)
