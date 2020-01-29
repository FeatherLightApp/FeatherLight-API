from starlette.testclient import TestClient
from app import app

def test_app():
    client = TestClient(app)

    create_user_query = """
    {
        create {
            ok
            error
            login
            password
        }
    }
    """
    res = client.post('/graphql/', json={'mutation': create_user_query})
    assert res.status_code == 200
    js = res.json()
    print(js)



test_app()
