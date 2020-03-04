"""custom scalars definition"""
from ariadne import ScalarType

JSON = ScalarType('JSON')

@JSON.serializer
def resolve_json(obj: dict, info) -> dict:
    info.context.logger.critical(f'json serializer {obj}')
    return obj
