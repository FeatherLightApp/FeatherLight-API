import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

@pytest.mark.usefixtures('dummy_user')
async def test_refresh_tokens(schema, context, dummy_user):
    context['request'].cookies = {'refresh': dummy_user['tokens']['refresh']}
    res = await graphql(
        schema,
        {
            'query': open('queries/refreshMacaroons.graphql').read()
        },
        context_value=context
    )
    r = res[1]['data']['refreshMacaroons']
    print(r)
    assert r['__typename'] == 'TokenPayload'
