# /project/helpers/io/locks.py
# Locks for file operations

import asyncio

_GUARD = asyncio.Lock()
_KEY_LOCK: dict[str, asyncio.Lock] = {}

class LockManager:
    """Manages locks."""
    
    async def get_lock(self, key: str) -> asyncio.Lock:
        """Gets a lock for a key."""
        async with _GUARD:
            return _KEY_LOCK.setdefault(key, asyncio.Lock())