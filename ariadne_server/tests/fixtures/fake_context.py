from secrets import token_hex
import pytest


class Object:
    pass


class FakeContext(dict):
    
    def __init__(self):
        req_obj = Object()
        req_obj.cookies = {}
        req_obj.client = Object()
        req_obj.client.host = token_hex(5)
        req_obj.headers = {'origin': 'some_origin'}

        self['request'] = req_obj



@pytest.fixture(autouse=True, scope='function')
def context():
    return FakeContext()