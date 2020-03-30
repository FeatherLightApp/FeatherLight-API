from datetime import datetime
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
    # set access token on header
    context['request'].headers['Authorization'] = dummy_user['tokens']['access']
    res = await graphql(
        schema,
        {
            'query': '''
                query me {
                    me {
                        created @date(format: "%m/%d/%Y, %H:%M:%S")
                    }
                }
            '''
        },
        context_value=context
    )
    r = res[1]['data']['me']
    assert r['created'] == datetime.fromtimestamp(dummy_user['created']).strftime("%m/%d/%Y, %H:%M:%S")