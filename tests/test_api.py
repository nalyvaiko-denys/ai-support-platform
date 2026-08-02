from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from redis.exceptions import ConnectionError

from app.db.redis import get_redis
from app.db.session import get_db
from app.dependencies.services import (
    get_chat_service,
)
from app.main import app


class FakeChatService:
    async def ask(
        self,
        owner_id: str,
        session_id: str,
        message: str,
    ) -> str:
        assert owner_id == "test-user"
        return f"Mock reply for {session_id}: {message}"

    async def get_history(
        self,
        owner_id: str,
        session_id: str,
        *,
        limit: int = 50,
    ) -> list[object]:
        assert owner_id == "test-user"
        del session_id, limit

        return []


class FakeDatabaseSession:
    def __init__(self) -> None:
        self.execute_count = 0

    async def execute(self, statement: object) -> None:
        del statement
        self.execute_count += 1


class FakeRedisPipeline:
    async def __aenter__(self) -> "FakeRedisPipeline":
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        del exc_type, exc_value, traceback

    def incr(self, key: str) -> None:
        assert key.startswith("rate-limit:chat:")

    def expire(self, key: str, seconds: int) -> None:
        del key
        assert seconds > 0

    async def execute(self) -> list[object]:
        return [1, True]


class FakeRedis:
    def pipeline(self, *, transaction: bool) -> FakeRedisPipeline:
        assert transaction is True
        return FakeRedisPipeline()

    async def ping(self) -> bool:
        return True


class UnavailableRedis(FakeRedis):
    async def ping(self) -> bool:
        raise ConnectionError("unavailable")


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    service = FakeChatService()
    database_session = FakeDatabaseSession()

    async def override_database() -> AsyncIterator[FakeDatabaseSession]:
        yield database_session

    app.dependency_overrides[get_chat_service] = lambda: service
    app.dependency_overrides[get_db] = override_database
    app.dependency_overrides[get_redis] = lambda: FakeRedis()

    token = jwt.encode(
        {
            "sub": "test-user",
            "iss": "ai-support-platform",
            "aud": "ai-support-api",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        "test-secret-that-is-long-enough-for-hs256",
        algorithm="HS256",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={
            "Authorization": f"Bearer {token}",
        },
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_accepts_valid_message(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/test-session",
        json={
            "message": "  How can I change my card PIN?  ",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["session_id"] == "test-session"
    assert payload["message"] == ("How can I change my card PIN?")
    assert "How can I change my card PIN?" in payload["reply"]


@pytest.mark.asyncio
async def test_rejects_blank_message(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/test-session",
        json={
            "message": "   ",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejects_extra_fields(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/test-session",
        json={
            "message": "Test",
            "unexpected": True,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == ("extra_forbidden")


@pytest.mark.asyncio
async def test_rejects_invalid_session_id(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/invalid.session",
        json={
            "message": "Test",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejects_missing_bearer_token(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/test-session",
        headers={
            "Authorization": "",
        },
        json={
            "message": "Test",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_returns_empty_history(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/test-session/history")

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "test-session",
        "messages": [],
    }


@pytest.mark.asyncio
async def test_liveness_check(client: AsyncClient) -> None:
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient) -> None:
    response = await client.get("/api/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_readiness_fails_when_redis_is_unavailable(
    client: AsyncClient,
) -> None:
    app.dependency_overrides[get_redis] = lambda: UnavailableRedis()

    response = await client.get("/api/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Application dependencies are not ready.",
    }
