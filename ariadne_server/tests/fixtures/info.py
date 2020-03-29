import pytest

class Object:
    pass


class FakeInfo:
    
    def __init__(self):
        req_obj = Object()
        req_obj.cookies = {}
        req_obj.client = Object()
        req_obj.client.host = 'some_ip_address'
        req_obj.headers ={}

        self.context = {
            'request': req_obj
        }


@pytest.fixture
def info():
    return FakeInfo()