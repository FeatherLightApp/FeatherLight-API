"""Class for locking Redis instance"""
from datetime.datetime import now

class Lock:

    def __init__(self, redis, lock_key):
        self._redis = redis
        self._lock_key = lock_key

    async def obtain_lock(self):
        timestamp = now()
        set_result = await this._redis.setnx(this._lock_key, timestamp)
        # fail if value already exists
        if not set_result:
            return False
        # expire lock after 5 mins as failsafe
        await this._redis.expire(this._lock_key, 5 * 60)
        # lock success
        return True

    async def release_lock(self):
        await this._redis.del(this._lock_key)