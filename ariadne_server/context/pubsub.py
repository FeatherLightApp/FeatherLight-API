import asyncio
from typing import Dict, List
from helpers.mixins import LoggerMixin

class StreamQueue(asyncio.Queue):
    """
    allow for streaming contents of queue via async generator
    """
    mark_closed = False

    async def __aiter__(self):
        while True:
            yield await self.get()
            if self.mark_closed and self.empty():
                raise GeneratorExit



class PubSubManager(LoggerMixin, Dict[str, List[StreamQueue]]):
    """
    Manager for pub/subbing to local invoice payments
    LND stub provides a way to sub to remotely paid invoices
    so we need to bride this functionality only for local invoices

    client id's are exposed as dict keys where values are a list of asyncio queues
    each queue represents a listener client
    """


    def add_client(self, userid: str) -> StreamQueue:
        """adds a queue to the list of queues and return it"""
        if userid in self.keys():
            self[userid].append(StreamQueue())
            return self[userid][-1]
        self[userid] = [StreamQueue()]
        return self[userid][-1]
