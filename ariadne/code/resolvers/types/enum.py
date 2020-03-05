from ariadne import EnumType
from code.classes.error import Error


ERROR_TYPE = EnumType('ErrorType', Error.get_type_dict())
