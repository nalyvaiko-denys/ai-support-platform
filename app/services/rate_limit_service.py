import hashlib
import time
from collections.abc import Callable

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.exceptions import (
    RateLimitBackendError,
    RateLimitExceededError,
)


class RateLimitService:
    def __init__(
        self,
        redis: Redis,
        *,
        request_limit: int,
        window_seconds: int,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.redis = redis
        self.request_limit = request_limit
        self.window_seconds = window_seconds
        self.clock = clock

    async def enforce(self, *, subject: str, scope: str) -> None:
        now = int(self.clock())
        window = now // self.window_seconds
        retry_after = self.window_seconds - (now % self.window_seconds)
        subject_hash = hashlib.sha256(subject.encode("utf-8")).hexdigest()
        key = f"rate-limit:{scope}:{subject_hash}:{window}"

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, retry_after + 1)
                results = await pipe.execute()
        except RedisError as exc:
            raise RateLimitBackendError from exc

        request_count = int(results[0])

        if request_count > self.request_limit:
            raise RateLimitExceededError(
                limit=self.request_limit,
                retry_after=retry_after,
            )
