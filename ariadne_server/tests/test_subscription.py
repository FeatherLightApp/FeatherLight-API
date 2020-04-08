from ariadne import subscribe
import pytest

pytestmark = pytest.mark.asyncio

@pytest.mark.usefixtures('dummy_user')
async def test_unauthed_subscription(schema, context, dummy_user):
    # context['request'].headers = {'Authorization': dummy_user['tokens']['access']}
    mapped = await subscribe(
        schema,
        {
            'query': open('queries/subscribe_invoices.graphql').read()
        },
        context_value=context
    )
    async for res in mapped[1]:
        print(res)
        r = res[0]['invoice']
        assert r['__typename'] == 'Error'


@pytest.mark.usefixtures('dummy_user')
async def test_authed_subscription(schema, context, dummy_user):
    context['request'].headers = {'Authorization': f"Bearer {dummy_user['tokens']['access']}"}
    mapped = await subscribe(
        schema,
        {
            'query': open('queries/subscribe_invoices.graphql').read()
        },
        context_value=context
    )
    async for res in mapped[1]:
        print(res)
