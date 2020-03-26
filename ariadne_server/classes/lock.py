"""Class for locking Redis instance"""
from datetime import datetime
from helpers.mixins import LoggerMixin
from context import REDIS


class Lock(LoggerMixin):
    """Class for locking redis db"""

    def __init__(self, lock_key):
        self._lock_key = lock_key

    async def obtain_lock(self):
        """obtain lock based on current time"""
        utc_seconds = (datetime.utcnow() -
                       datetime(1970, 1, 1)).total_seconds()
        set_result = await REDIS.conn.setnx(self._lock_key, utc_seconds)
        self.logger.critical(f"set result {set_result}")
        # fail if value already exists
        if not set_result:
            return False
        # expire lock after 5 mins as failsafe
        await REDIS.conn.expire(self._lock_key, 5 * 60)
        # lock success
        return True

    async def release_lock(self):
        """release obtained lock"""
        await REDIS.conn.delete(self._lock_key)
