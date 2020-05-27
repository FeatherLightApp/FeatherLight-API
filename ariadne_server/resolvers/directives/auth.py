"""Module to define directive for valiadtion user requests"""
from asyncio import iscoroutinefunction
from typing import Union, Optional, Tuple
from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from pymacaroons import Macaroon
from pymacaroons.exceptions import (
    MacaroonDeserializationException,
    MacaroonInvalidSignatureException
)
from classes import Error, User
from models import LSAT
from helpers.mixins import LoggerMixin
from helpers.crypto import verify


class AuthDirective(SchemaDirectiveVisitor, LoggerMixin):
    """Directive class"""
    def __init__(self, *args):
        super().__init__(*args)
        self.get_auth = None
        # Determine how to retrieve credentials and preimage, if applicable

        #define refresh macaroon retrieval 
        if 'REFRESH' in self.args.get('caveats'):
            def get_auth(info) -> Tuple[Optional[str], Optional[str]]:
                return info.context['request'].cookies.get('refresh'), None 

        #define lsat retrieval with preimage
        elif 'LSAT' in self.args.get('kind'):
            def get_auth(info) -> Tuple[Optional[str], Optional[str]]:
                auth = info.context['request'].headers.get('Authorization')
                if not auth:
                    return None, None
                data = auth.replace('LSAT ', '').split(':')
                return data[0], data[1]
        
        # define standard access macaroon retrieval
        else:
            def get_auth(info) -> Tuple[Optional[str], Optional[str]]:
                """helper to correctly retrieve access macaroon from req headers"""
                auth = info.context['request'].headers.get('Authorization')
                if not auth:
                    return None, None
                return auth.replace('Bearer ', ''), None
        
        self.get_auth = get_auth


    async def check_auth(self, info) -> Union[User, LSAT, Error]:
        """Function to check authentication of user"""
        # check if auth header is present
        serial_macaroon, preimage = self.get_auth(info)
        if not serial_macaroon:
            return Error('NoCredentials', 'No token sent. You are not logged in')
        # attempt to deserialize macaroon
        try:
            macaroon = Macaroon.deserialize(serial_macaroon)
        except MacaroonDeserializationException:
            return Error('AuthenticationError', 'Invalid token sent')

        # define types needed
        macaroon_key: bytes
        payload: Union[User, LSAT]
        # determine if auth is an lsat
        if 'LSAT' in self.args.get('kind'):
            lsat: Optional[LSAT] = await LSAT.get(macaroon.identifier)
            if not lsat:
                return Error('AuthenticationError', 'Could not find lsat')
            if not preimage or preimage != lsat.preimage:
                return Error('AuthenticationError', 'Invalid preimage')
            macaroon_key = lsat.key
            payload = lsat

        # auth is standard macaroon
        else:
            # lookup user by identifier
            db_user: Optional[User] = await User.get(macaroon.identifier)
            if not db_user:
                return Error('AuthenticationError', 'Could not find user')
            macaroon_key = db_user.key
            payload = db_user

        # verify macaroon against directive arguments
        try:
            verify(
                macaroon=macaroon,
                key=macaroon_key,
                roles=self.args.get('roles'),
                caveats=self.args.get('caveats'),
                req=info.context['request']
            )
        except MacaroonInvalidSignatureException:
            return Error('AuthenticationError', 'Macaroon caveats not satisfied')

        return payload


    def visit_field_definition(self, field, object_type):
        orig_resolver = field.resolve or default_field_resolver
        is_subscription = getattr(field, 'subscribe', None)

        if is_subscription:
            orig_source = field.subscribe
            #source gen
            async def gen(_, info, **kwargs):

                root = await self.check_auth(info)
                if isinstance(root, Error):
                    yield root
                    return
                async for item in orig_source(root, info, **kwargs):
                    yield item
            field.subscribe = gen
        else:
            async def call(_, info, **kwargs):
                root = await self.check_auth(info)
                # if auth is invalid return error to union resolver
                if isinstance(root, Error):
                    return root

                # attempt to pass user into root resolver
                if iscoroutinefunction(orig_resolver):
                    return await orig_resolver(root, info, **kwargs)
                else:
                    return orig_resolver(root, info, **kwargs)

            field.resolve = call
            
        return field