import pytest
from redis.exceptions import ConnectionError

from app.core.exceptions import (
    RateLimitBackendError,
    RateLimitExceededError,
)
from app.services.rate_limit_service import RateLimitService


class FakePipeline:
    def __init__(
        self,
        *,
        request_count: int,
        failure: Exception | None = None,
    ) -> None:
        self.request_count = request_count
        self.failure = failure
        self.keys: list[str] = []
        self.expiration_seconds = 0

    async def __aenter__(self) -> "FakePipeline":
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        del exc_type, exc_value, traceback

    def incr(self, key: str) -> None:
        self.keys.append(key)

    def expire(self, key: str, seconds: int) -> None:
        self.keys.append(key)
        self.expiration_seconds = seconds

    async def execute(self) -> list[object]:
        if self.failure is not None:
            raise self.failure

        return [self.request_count, True]


class FakeRedis:
    def __init__(self, pipeline: FakePipeline) -> None:
        self.fake_pipeline = pipeline

    def pipeline(self, *, transaction: bool) -> FakePipeline:
        assert transaction is True
        return self.fake_pipeline


def create_service(pipeline: FakePipeline) -> RateLimitService:
    return RateLimitService(
        FakeRedis(pipeline),
        request_limit=3,
        window_seconds=60,
        clock=lambda: 125.0,
    )


@pytest.mark.asyncio
async def test_allows_request_within_limit() -> None:
    pipeline = FakePipeline(request_count=3)
    service = create_service(pipeline)

    await service.enforce(subject="customer-1", scope="chat")

    assert pipeline.keys[0] == pipeline.keys[1]
    assert "customer-1" not in pipeline.keys[0]
    assert pipeline.expiration_seconds == 56


@pytest.mark.asyncio
async def test_rejects_request_above_limit() -> None:
    service = create_service(FakePipeline(request_count=4))

    with pytest.raises(RateLimitExceededError) as error:
        await service.enforce(subject="customer-1", scope="chat")

    assert error.value.limit == 3
    assert error.value.retry_after == 55


@pytest.mark.asyncio
async def test_fails_closed_when_redis_is_unavailable() -> None:
    service = create_service(
        FakePipeline(
            request_count=0,
            failure=ConnectionError("unavailable"),
        )
    )

    with pytest.raises(RateLimitBackendError):
        await service.enforce(subject="customer-1", scope="chat")
