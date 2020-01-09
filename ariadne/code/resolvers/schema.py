"""import and define schem execution"""
from ariadne import load_schema_from_path
from ariadne import make_executable_schema
from .types import types 

type_defs = load_schema_from_path('code/schema/')

schema = make_executable_schema(type_defs, types)
