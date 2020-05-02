from typing import Optional
from ariadne import QueryType
from context import LND
import rpc_pb2 as ln

QUERY = QueryType()

class ChannelResponse:
    """class to define functional responses to channels query"""    
    async def open_channels(
        self,
        *_,
        active: bool = False,
        inactive: bool = False,
        public: bool = False,
        private: bool = False,
        peer: Optional[bytes] = None
    ):
        req = ln.ListChannelsRequest(
            active_only=active,
            inactive_only=inactive,
            public_only=public,
            private_only=private
        )
        r = await LND.stub.ListChannels(req)
        return r.channels

    async def pending_channels(self, *_):
        req = ln.PendingChannelsRequest()
        return await LND.stub.PendingChannels(req)

@QUERY.field('channels')
async def r_channels(*_):
    return ChannelResponse()