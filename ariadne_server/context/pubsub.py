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

    def add_client(self, userid):
        """adds a queue to the list of queues and returns the index"""
        if userid in self.keys():
            self[userid].append(StreamQueue())
            return len(self[userid]) - 1
        self[userid] = [StreamQueue()]
        return 0
        
    def close_client(self, userid, index):
        """
        removes specified queue from list of queues
        if it is the last queue in the list then the key is removed from dict
        """
        del self[userid][index]
        # remove dangling userid if it is empty
        if len(self[userid]) == 0:
            del self[userid]

    async def initialize(self):
        """
        start streaming background tasks, these tasks allow for db objects
        to be returned to user then written to db asynchronously in background
        """
        async with streamcontext(self.background_tasks) as stream:
            async for fn in stream():
                await fn()



    

    


