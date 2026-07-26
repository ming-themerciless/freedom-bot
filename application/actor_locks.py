from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from inspect import signature
from weakref import WeakValueDictionary


class ActorLockManager:
    """Serializes mutations for actors within one running bot process."""

    def __init__(self) -> None:
        self._locks: WeakValueDictionary[str, asyncio.Lock] = WeakValueDictionary()
        self._registry_lock = asyncio.Lock()

    @staticmethod
    def _key(actor_name: str) -> str:
        return actor_name.strip().casefold()

    async def _get_lock(self, actor_name: str) -> asyncio.Lock:
        key = self._key(actor_name)
        async with self._registry_lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[key] = lock
            return lock

    @asynccontextmanager
    async def acquire(self, *actor_names: str):
        keys = sorted({self._key(name) for name in actor_names if self._key(name)})
        locks = [await self._get_lock(key) for key in keys]
        for lock in locks:
            await lock.acquire()
        try:
            yield
        finally:
            for lock in reversed(locks):
                lock.release()


actor_locks = ActorLockManager()


def locked_actor_option(parameter: str = "actor_name"):
    """Lock a command for the actor-name argument while it executes."""

    def decorate(function):
        function_signature = signature(function)

        @wraps(function)
        async def wrapped(*args, **kwargs):
            bound = function_signature.bind(*args, **kwargs)
            actor_name = bound.arguments[parameter]
            async with actor_locks.acquire(actor_name):
                return await function(*args, **kwargs)

        return wrapped

    return decorate
