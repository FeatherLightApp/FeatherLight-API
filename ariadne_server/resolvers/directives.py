import inspect
from typing import Union, Dict
from asyncio import iscoroutinefunction
from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from helpers.crypto import decode
from classes.user import User
from classes.error import Error
from helpers.mixins import LoggerMixin
from context import REDIS


class AuthDirective(SchemaDirectiveVisitor, LoggerMixin):

    def visit_field_definition(self, field, *_):
        # req_role = self.args.get('requires') TODO Implement roles later
        orig_resolver = field.resolve or default_field_resolver

        # define wrapper
        async def check_auth(obj, info, **kwargs):
            if not (auth_header:= info.context['request'].headers.get('Authorization')):
                return Error('AuthenticationError', 'No access token sent. You are not logged in')
            decode_response: Union[Dict, Error] = decode(
                auth_header.replace('Bearer ', ''), kind='access')
            # if decode fails return the error
            if isinstance(decode_response, Error):
                return decode_response
            if self.args.get('requires') == 'ADMIN' and decode_response['role'] != 'ADMIN':
                return Error('AuthenticationError', 'You do not have permission to do this')
            # User is authenticated. Inject into obj if not defined
            db_user = await User.get(decode_response['id'])
            self.logger.critical(db_user)
            new_obj = obj or db_user
            self.logger.critical(new_obj)
            if iscoroutinefunction(orig_resolver):
                result = await orig_resolver(new_obj, info, **kwargs)
            else:
                result = orig_resolver(new_obj, info, **kwargs)
            self.logger.critical(f"result {result}")
            return result

        field.resolve = check_auth
        return field


class DatetimeDirective(SchemaDirectiveVisitor):

    def visit_field_definition(self, field, *_):
        orig_resolver = field.resolve or default_field_resolver
        date_format = self.args.get('format') or self.args.get('defaultFormat')

        def resolve_formatted_date(obj, info, **kwargs):
            result = orig_resolver(obj, info, **kwargs)
            if result is None:
                return None

            return result.strftime(date_format)
        field.resolve = resolve_formatted_date
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

            return Error('RateLimited', f"You have exceeded rate limit of {operations} requests per {seconds} seconds")

        field.resolve = check_rate_limit
        return field
