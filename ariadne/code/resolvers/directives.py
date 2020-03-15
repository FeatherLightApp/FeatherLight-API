from typing import Union, Dict
from asyncio import iscoroutinefunction
from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from code.helpers.crypto import decode
from code.classes.user import User
from code.classes.error import Error
from code.helpers.mixins import LoggerMixin
import inspect

class AuthDirective(SchemaDirectiveVisitor, LoggerMixin):

    def visit_field_definition(self, field, object_type=None):
        #req_role = self.args.get('requires') TODO Implement roles later
        orig_resolver = field.resolve or default_field_resolver

        #define wrapper
        async def check_auth(obj, info, **kwargs):
            if not (auth_header := info.context.req.headers.get('Authorization')):
                return Error('AuthenticationError', 'No access token sent. You are not logged in')
            decode_response: Union[Dict, Error] = decode(auth_header.replace('Bearer ', ''), kind='access')
            # if decode fails return the error
            if isinstance(decode_response, Error):
                return decode_response
            # User is authenticated. Inject into obj if not defined
            new_obj = obj or User(decode_response['id'])
            if iscoroutinefunction(orig_resolver):
                return await orig_resolver(new_obj, info, **kwargs)
            else:
                return orig_resolver(new_obj, info, **kwargs)
        
        field.resolve = check_auth
        return field
