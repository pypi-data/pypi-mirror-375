from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Set


@dataclass(slots=True)
class Event:
    """Generic event container for the bus. Extend or replace as needed."""
    topic: str
    payload: Any


class Subscription:
    def __init__(self, topic: str, queue: asyncio.Queue, cancel_cb):
        self.topic = topic
        self.queue = queue
        self._cancel_cb = cancel_cb

    async def __anext__(self):
        item = await self.queue.get()
        if item is StopAsyncIteration:
            raise StopAsyncIteration
        return item

    def __aiter__(self) -> AsyncIterator[Any]:
        return self

    def unsubscribe(self) -> None:
        self._cancel_cb(self)


class EventBus:
    """A minimal asyncio-based pub/sub event bus with bounded queues.

    - Subscribers receive events for a specific topic via their own queue.
    - If a subscriber's queue is full, the event is dropped for that subscriber to
      avoid backpressure cascading (can be made configurable later).
    - `close()` gracefully stops the bus and unblocks subscribers.
    """

    def __init__(self, default_queue_size: int = 1024):
        self._topics: Dict[str, Set[Subscription]] = defaultdict(set)
        self._default_qsize = default_queue_size
        self._closed = False
        self._lock = asyncio.Lock()
        self.dropped = 0

    async def subscribe(self, topic: str, *, max_queue: int | None = None) -> Subscription:
        if self._closed:
            raise RuntimeError("EventBus is closed")
        q = asyncio.Queue(maxsize=max_queue or self._default_qsize)

        def _cancel_cb(sub: Subscription) -> None:
            subs = self._topics.get(topic)
            if subs and sub in subs:
                subs.remove(sub)

        sub = Subscription(topic, q, _cancel_cb)
        async with self._lock:
            self._topics[topic].add(sub)
        return sub

    async def publish(self, topic: str, payload: Any) -> None:
        if self._closed:
            return
        event = Event(topic=topic, payload=payload)
        # Copy to avoid iteration issues if set mutates
        async with self._lock:
            subs = list(self._topics.get(topic, ()))
        for sub in subs:
            try:
                sub.queue.put_nowait(event)
            except asyncio.QueueFull:
                self.dropped += 1
                # drop for that subscriber
                continue

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        async with self._lock:
            for subs in self._topics.values():
                for sub in list(subs):
                    try:
                        sub.queue.put_nowait(StopAsyncIteration)
                    except asyncio.QueueFull:
                        # best-effort unblock
                        pass
            self._topics.clear()

