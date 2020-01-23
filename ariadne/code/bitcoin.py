"""Class for running bitcoin rpc requests"""
from secrets import token_hex
from httpx import AsyncClient
from code.helpers.mixins import LoggerMixin

class Bitcoin(AsyncClient, LoggerMixin):
    """Subclass for making btcd rpc requests"""
    def __init__(self, config):
        LoggerMixin()
        self._host = config['host']
        self._port = config['port']
        self._user = config['user']
        self._pass = config['pass']

    async def req(self, method, params=None, reqid=None):
        """make a request to bitcoin rpc and return response json sync"""
        url = f'http://{self._host}:{self._port}'
        self.logger.critical(url)
        js = {'method': method}
        if params:
            js['params'] = params
        js['id'] = reqid if reqid else token_hex(4)
        async with AsyncClient() as client:
            res = await client.post(
                url,
                json=js,
                auth=(self._user, self._pass),
                headers={'Content-Type': 'application/json'}
            )
            return res.json()
