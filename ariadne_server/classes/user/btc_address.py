import asyncio
from helpers.mixins import LoggerMixin
from context import BITCOIND, LND
import rpc_pb2 as ln
from .abstract_user_method import AbstractMethod


class GetBTCAddress(AbstractMethod, LoggerMixin):
    """method to get btc address"""
    async def run(self, user):
        """
        return bitcoin address of user. If the address does not exist
        asynchronously generate a new lightning address
        gRPC Response: NewAddressResponse
        see https://api.lightning.community/#newaddress
        for more info

        """
        # return address if it exists
        if address := user.bitcoin_address:
            return address

        #  create a new address
        request = ln.NewAddressRequest(type=0)
        response = await LND.stub.NewAddress(request)
        address = response.address
        update = user.update(bitcoin_address=address)
        # delegate db write
        loop = asyncio.get_running_loop()
        loop.create_task(update.apply())
        self.logger.warning("Created address: %s for user: %s", address, user.username)
        await BITCOIND.req(
            'importaddress',
            params={
                'address': address,
                'label': user.username,
                'rescan': False
            }
        )
        return address
