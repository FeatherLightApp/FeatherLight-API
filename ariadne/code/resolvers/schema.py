"""import and define schem execution"""
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers
)
from .types import TYPES

TYPE_DEFS = load_schema_from_path('code/schema/')

SCHEMA = make_executable_schema(TYPE_DEFS, TYPES, snake_case_fallback_resolvers)
