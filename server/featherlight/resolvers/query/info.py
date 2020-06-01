from ariadne import QueryType
from context import LND
from proto import rpc_pb2 as ln


QUERY = QueryType()


@QUERY.field("info")
# @authenticate
async def r_info(*_) -> dict:
    request = ln.GetInfoRequest()
    return await LND.stub.GetInfo(request)
