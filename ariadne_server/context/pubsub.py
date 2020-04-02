import asyncio
from helpers.mixins import LoggerMixin
from aiostream import streamcontext

class StreamQueue(asyncio.Queue):
    """
    allow for streaming contents of queue via async generator
    """
    async def __aiter__(self):
        while True:
            yield await self.get()


class PubSubManager(LoggerMixin, dict):
    """
    Manager for pub/subbing to local invoice payments
    LND stub provides a way to sub to remotely paid invoices
    so we need to bride this functionality only for local invoices

    client id's are exposed as dict keys where values are a list of asyncio queues
    each queue represents a listener client
    """

    def __init__(self):
        self.background_tasks = StreamQueue()
        self.stream= None

    def add_client(self, userid):
        """adds a queue to the list of queues and return it along with its index"""
        if userid in self.keys():
            self[userid].append(StreamQueue())
            return self[userid][-1]
        self[userid] = [StreamQueue()]
        return self[userid][-1], 0


    async def initialize(self):
        """
        start streaming background tasks, these tasks allow for db objects
        to be returned to user then written to db asynchronously in background
        """
        async with streamcontext(self.background_tasks) as self.stream:
            async for fctn in stream():
                await fctn()

    async def destroy(self):
        if self.stream:
            self.stream.throw()



    

    


