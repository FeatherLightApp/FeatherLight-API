import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

@pytest.mark.usefixtures('dummy_user')
async def test_query_myself(schema, context, dummy_user):
    context['request'].headers['Authorization'] = f"Bearer {dummy_user['tokens']['access']}"
    res = await graphql(
        schema,
        {
            'query': open('queries/me.graphql').read()
        },
        context_value=context
    )
    print(res)
    r = res[1]['data']['me']
    assert r['__typename'] == 'User'