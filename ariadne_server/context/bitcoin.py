import os
from secrets import token_hex
from httpx import AsyncClient
from ..helpers.mixins import LoggerMixin

class BitcoinClient(AsyncClient, LoggerMixin):
    """Subclass for making btcd rpc requests"""
    def __init__(self):
        self._host = os.environ.get('BITCOIND_HOST')
        self._port = os.environ.get('BITCOIND_PORT')
        self._user = os.environ.get('BITCOIND_USER')
        self._pass = os.environ.get('BITCOIND_PASSWORD')

    async def req(self, method: str, params=None, reqid=None):
        """make a request to bitcoin rpc and return response json"""
        url = f'http://{self._host}:{self._port}'
        self.logger.info(f"making request to: {url}")
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


BITCOIND = BitcoinClient()
