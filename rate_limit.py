"""Small dependency-free rate limiter for the demo API.

The limiter is intentionally process-local. Use a shared store such as Redis when
running more than one API worker or more than one instance.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class Bucket:
    started_at: float
    requests: int = 0


class FixedWindowRateLimiter:
    """Limit each client key to ``limit`` requests per time window."""

    def __init__(self, limit: int = 60, window_seconds: int = 60, clock=time.monotonic):
        if limit < 1 or window_seconds < 1:
            raise ValueError("limit and window_seconds must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._buckets: dict[str, Bucket] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> tuple[bool, dict[str, str]]:
        """Consume one request and return ``(allowed, headers)``."""
        now = self._clock()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None or now - bucket.started_at >= self.window_seconds:
                bucket = Bucket(started_at=now)
                self._buckets[key] = bucket
            bucket.requests += 1
            remaining = max(self.limit - bucket.requests, 0)
            reset_in = max(self.window_seconds - (now - bucket.started_at), 0)
            allowed = bucket.requests <= self.limit
        return allowed, {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(reset_in)),
            "Retry-After": str(max(int(reset_in), 1)),
        }

    def reset(self) -> None:
        """Clear all buckets; useful for tests and controlled maintenance."""
        with self._lock:
            self._buckets.clear()
