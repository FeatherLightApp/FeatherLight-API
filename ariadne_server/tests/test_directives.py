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

async def _get_node_balance(schema, context):
    res = await graphql(
        schema,
        {
            'query': open('queries/nodeBalance.graphql').read()
        },
        context_value=context
    )
    r = res[1]['data']['nodeBalance']
    print(r)
    return r

@pytest.mark.usefixtures('dummy_user', 'dummy_admin')
async def test_valid_auth(schema, context, dummy_admin):
    print(dummy_admin['tokens']['access'])
    context['request'].headers = {
        'Authorization': f'Bearer {dummy_admin["tokens"]["access"]}'
    }
    r = await _get_node_balance(schema, context)
    assert r['__typename'] == 'NodeBalance'


async def test_invalid_auth(schema, context, dummy_user):
    print(dummy_user['tokens']['access'])
    context['request'].headers = {
        'Authorization': f'Bearer {dummy_user["tokens"]["access"]}'
    }
    r = await _get_node_balance(schema, context)
    assert r['__typename'] == 'Error'
