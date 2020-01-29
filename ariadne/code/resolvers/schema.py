"""import and define schem execution"""
from ariadne import load_schema_from_path, make_executable_schema, snake_case_fallback_resolvers
from .types import types 

type_defs = load_schema_from_path('code/schema/')

schema = make_executable_schema(type_defs, types, snake_case_fallback_resolvers)
