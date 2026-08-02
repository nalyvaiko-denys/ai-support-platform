from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.core.auth import CurrentUser
from app.core.config import settings
from app.db.redis import get_redis
from app.services.rate_limit_service import RateLimitService

RedisClient = Annotated[
    Redis,
    Depends(get_redis),
]


def get_rate_limit_service(
    redis: RedisClient,
) -> RateLimitService:
    return RateLimitService(
        redis,
        request_limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


RateLimitServiceDep = Annotated[
    RateLimitService,
    Depends(get_rate_limit_service),
]


async def enforce_chat_rate_limit(
    current_user: CurrentUser,
    rate_limit_service: RateLimitServiceDep,
) -> None:
    await rate_limit_service.enforce(
        subject=current_user.subject,
        scope="chat",
    )


ChatRateLimit = Annotated[
    None,
    Depends(enforce_chat_rate_limit),
]
