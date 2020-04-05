"""Hotfix for manually writing enum types"""
from ariadne import EnumType

_action = EnumType(
    'Action',
    {
        'ADD_INVOICE': 'ADD_INVOICE',
        'READ_BALANCE': 'READ_BALANCE'
    }
)

_use_type = EnumType(
    'UseType',
    {
        'ACCESS': 'ACCESS',
        'REFRESH': 'REFRESH'
    }
)

_role = EnumType(
    'Role',
    {
        'USER': 'USER',
        'ADMIN': 'ADMIN'
    }
)

EXPORT = [
    _action,
    _use_type,
    _role
]