import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

# Query is too low level to test returned cookie responses
# Make actual http request to starlette to test cookies
@pytest.mark.usefixtures('dummy_user')
async def test_refresh_tokens(schema, context, dummy_user):
    context['request'].cookies = {'refresh': dummy_user['tokens']['refresh']}
    context['request'].headers = {'origin': 'some_origin'}
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


@pytest.mark.usefixtures('dummy_user')
async def test_malicious_refresh_tokens(schema, context, dummy_user):
    context['request'].cookies = {'refresh': dummy_user['tokens']['refresh']}
    context['request'].headers = {'origin': 'malicious_origin'}
    res = await graphql(
        schema,
        {
            'query': open('queries/refreshMacaroons.graphql').read()
        },
        context_value=context
    )
    r = res[1]['data']['refreshMacaroons']
    print(r)
    assert r['__typename'] == 'Error'