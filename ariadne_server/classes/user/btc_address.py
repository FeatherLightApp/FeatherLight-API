from .abstract_user_method import AbstractMethod
from helpers.mixins import LoggerMixin
from helpers.async_future import make_async
from context import BITCOIND, LND
import rpc_pb2 as ln


class GetBTCAddress(AbstractMethod, LoggerMixin):

    async def run(self, user):
        """
        return bitcoin address of user. If the address does not exist
        asynchronously generate a new lightning address
        gRPC Response: NewAddressResponse
        see https://api.lightning.community/#newaddress
        for more info

        """
        # return address if it exists
        if (address:= user.bitcoin_address):
            return address

        #  create a new address
        request = ln.NewAddressRequest(type=0)
        response = await make_async(LND.stub.NewAddress.future(request, timeout=5000))
        address = response.address
        await user.update(bitcoin_address=address).apply()
        self.logger.info(f"Created address: {address} for user: {user.id}")
        import_response = await BITCOIND.req(
            'importaddress',
            params={
                'address': address,
                'label': user.id,
                'rescan': False
            }
        )
        return address
