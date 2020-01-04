"""import and define schem execution"""
from ariadne import load_schema_from_path
from ariadne import make_executable_schema
from code.resolvers.Query import query
from code.resolvers.Mutation import mutation

type_defs = load_schema_from_path('code/schema/')

schema = make_executable_schema(
    type_defs,
    [
        query,
        mutation
    ]
)
