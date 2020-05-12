import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

async def test_rate_limit(schema, context):
    context['request'].headers['x-real-ip'] = 'newip'
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
    print(res)
    r = res[1]['data']['nodeBalance']
    return r

@pytest.mark.usefixtures('dummy_admin')
async def test_valid_role(schema, context, dummy_admin):
    context['request'].headers['Authorization'] = f'Bearer {dummy_admin["tokens"]["access"]}'
    r = await _get_node_balance(schema, context)
    print(r)
    assert r['__typename'] == 'NodeBalance'


@pytest.mark.usefixtures('dummy_user')
async def test_invalid_role(schema, context, dummy_user):
    context['request'].headers['Authorization'] = f'Bearer {dummy_user["tokens"]["access"]}'
    r = await _get_node_balance(schema, context)
    assert r['__typename'] == 'Error'
