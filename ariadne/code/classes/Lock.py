"""Class for locking Redis instance"""
from datetime import datetime

class Lock:
    """Class for locking redis db"""
    def __init__(self, redis, lock_key):
        self._redis = redis
        self._lock_key = lock_key

    async def obtain_lock(self):
        """obtain lock based on current time"""
        utc_seconds = (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        set_result = await self._redis.setnx(self._lock_key, utc_seconds)
        # fail if value already exists
        if not set_result:
            return False
        # expire lock after 5 mins as failsafe
        await self._redis.expire(self._lock_key, 5 * 60)
        # lock success
        return True

    async def release_lock(self):
        """release obtained lock"""
        await self._redis.delete(self._lock_key)
