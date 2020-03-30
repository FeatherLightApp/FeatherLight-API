import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

async def test_rate_limit(schema, context):
    for i in range(5):
        res = await graphql(
            schema,
            {
                'query': open('queries/createUser.graphql').read()
            },
            context_value=context
        )
        r = res[1]['data']['createUser']
        if i >= 3:
            assert r['errorType'] == 'RateLimited'
        else:
            assert r['username']
            assert r['password']



@pytest.mark.usefixtures('dummy_user')
async def test_datetime_formatting(schema, context, dummy_user):
    