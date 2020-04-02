import asyncio
from helpers.mixins import LoggerMixin
from aiostream import streamcontext

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
        self._task_loop = None

    def add_client(self, userid):
        """adds a queue to the list of queues and return it along with its index"""
        if userid in self.keys():
            self[userid].append(StreamQueue())
            return self[userid][-1]
        self[userid] = [StreamQueue()]
        return self[userid][-1], 0


    def initialize(self):
        """
        start streaming background tasks, these tasks allow for db objects
        to be returned to user then written to db asynchronously in background
        """
        async def run_loop():
            async with streamcontext(self.background_tasks) as stream:
                async for fctn in stream():
                    await fctn()

        self._task_loop = asyncio.create_task(run_loop())

    async def destroy(self):
        #mark loop for closure on completion
        self.background_tasks.mark_closed = True
        # await loop to close
        await self._task_loop
