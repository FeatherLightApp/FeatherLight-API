import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

logout_query = open('queries/logout.graphql').read()

@pytest.mark.usefixtures('dummy_user')
async def test_logout(schema, context, dummy_user):
    context['request'].headers['Authorization'] = f"Bearer {dummy_user['tokens']['access']}"
    response = await graphql(
        schema,
        {
            'query': logout_query
        },
        context_value=context,
        debug=True
    )
    r = response[1]['data']['logout']
    assert r is None

@pytest.mark.usefixtures('dummy_user')
async def test_reuse_old_token(schema, context, dummy_user):
    context['request'].headers['Authorization'] = f"Bearer {dummy_user['tokens']['access']}"
    response = await graphql(
        schema,
        {
            'query': logout_query
        },
        context_value=context,
        debug=True
    )
    r = response[1]['data']['logout']
    assert r['errorType'] == 'AuthenticationError'

