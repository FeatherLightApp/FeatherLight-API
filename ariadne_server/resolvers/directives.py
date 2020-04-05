from typing import Union, Dict
from asyncio import iscoroutinefunction
from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from pymacaroons import Macaroon
from pymacaroons.exceptions import (
    MacaroonDeserializationException,
    MacaroonInvalidSignatureException
)
from helpers.crypto import verify
from classes.user import User
from classes.error import Error
from helpers.mixins import LoggerMixin
from context import REDIS


class AuthDirective(SchemaDirectiveVisitor, LoggerMixin):

    def visit_field_definition(self, field, *_):
        orig_resolver = field.resolve or default_field_resolver

        # determine scoping of directive and set token retrieval accordingly
        if 'REFRESH' in self.args.get('actions'):
            get_macaroon = lambda info: info.context['request'].cookies.get('refresh')
        else:
            get_macaroon = lambda info: info.context['request'].headers.get('Authorization').replace('Bearer ', '')

        # define wrapper
        async def check_auth(obj, info, **kwargs):
            # check if auth header is present
            if not (serial_macaroon:= get_macaroon(info)):
                return Error('AuthenticationError', 'No access token sent. You are not logged in')
            # attempt to deserialize macaroon
            try:
                macaroon = Macaroon.deserialize(serial_macaroon)
            except MacaroonDeserializationException:
                return Error('AuthenticationError', 'Invalid token sent')
            
            # lookup user by identifier
            if not (db_user := await User.get(macaroon.identifier)):
                return Error('AuthenticationError', 'Could not find user')

            # verify macaroon against directive arguments
            try:
                verification = verify(
                    macaroon=macaroon,
                    key=db_user.key,
                    roles=self.args.get('roles'),
                    actions=self.args.get('actions'),
                )
                self.logger.critical(f'verify returned {verification}')
            except MacaroonInvalidSignatureException:
                return Error('AuthenticationError', 'You do not have the permission to do that')

            # User is authenticated. Inject into union resolver
            return db_user

        field.resolve = check_auth
        return field


class RatelimitDirective(SchemaDirectiveVisitor, LoggerMixin):

    def visit_field_definition(self, field, *_):
        orig_resolver = field.resolve or default_field_resolver
        operations = self.args.get('operations')
        seconds = self.args.get('seconds')
        key = self.args.get('limitKey')

        async def check_rate_limit(obj, info, **kwargs):
            redis_key = f"{key}_{info.context['request'].client.host}"
            num_requests = await REDIS.conn.get(redis_key)
            if not num_requests or int(num_requests) < operations:
                await REDIS.conn.incr(redis_key)
                if not num_requests:
                    await REDIS.conn.expire(redis_key, seconds)

                # resolve function
                if iscoroutinefunction(orig_resolver):
                    return await orig_resolver(obj, info, **kwargs)
                else:
                    return orig_resolver(obj, info, **kwargs)

            return Error(
                'RateLimited',
                f"You have exceeded rate limit of {operations} requests per {seconds} seconds"
            )

        field.resolve = check_rate_limit
        return field
