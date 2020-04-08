from asyncio import iscoroutinefunction
from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from context import REDIS
from classes.error import Error
from helpers.mixins import LoggerMixin

class RatelimitDirective(SchemaDirectiveVisitor, LoggerMixin):

    def visit_field_definition(self, field, object_type):
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