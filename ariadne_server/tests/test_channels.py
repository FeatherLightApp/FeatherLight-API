import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

@pytest.mark.usefixtures('dummy_user')
async def test_invalid_user(schema, context, dummy_user):
    context['request'].headers['Authorization'] = f'Bearer {dummy_user["tokens"]["access"]}'
    res = await graphql(
        schema,
        {
            'query': open('queries/channels.graphql').read()
        },
        context_value=context
    )
    print(res)
    r = res[1]['data']['channels']
    assert r['__typename'] == 'Error'
    assert r['errorType'] == 'AuthenticationError'

@pytest.mark.usefixtures('dummy_admin')
async def test_valid_user(schema, context, dummy_admin):
    context['request'].headers['Authorization'] = f'Bearer {dummy_admin["tokens"]["access"]}'
    res = await graphql(
        schema,
        {
            'query': open('queries/channels.graphql').read()
        },
        context_value=context
    )
    r = res[1]['data']['channels']
    assert r['__typename'] == 'ChannelPayload'
