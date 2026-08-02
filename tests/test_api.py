from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.dependencies.services import (
    get_chat_service,
)
from app.main import app


class FakeChatService:
    async def ask(
        self,
        session_id: str,
        message: str,
    ) -> str:
        return f"Mock reply for {session_id}: {message}"

    async def get_history(
        self,
        session_id: str,
        *,
        limit: int = 50,
    ) -> list[object]:
        del session_id, limit

        return []


class FakeDatabaseSession:
    def __init__(self) -> None:
        self.execute_count = 0

    async def execute(self, statement: object) -> None:
        del statement
        self.execute_count += 1


@pytest.fixture
def client() -> Iterator[TestClient]:
    service = FakeChatService()
    database_session = FakeDatabaseSession()

    async def override_database() -> AsyncIterator[FakeDatabaseSession]:
        yield database_session

    app.dependency_overrides[get_chat_service] = lambda: service
    app.dependency_overrides[get_db] = override_database

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_accepts_valid_message(
    client: TestClient,
) -> None:
    response = client.post(
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


def test_rejects_blank_message(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/test-session",
        json={
            "message": "   ",
        },
    )

    assert response.status_code == 422


def test_rejects_extra_fields(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/test-session",
        json={
            "message": "Test",
            "unexpected": True,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == ("extra_forbidden")


def test_rejects_invalid_session_id(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/invalid.session",
        json={
            "message": "Test",
        },
    )

    assert response.status_code == 422


def test_returns_empty_history(
    client: TestClient,
) -> None:
    response = client.get("/api/test-session/history")

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "test-session",
        "messages": [],
    }


def test_liveness_check(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check(client: TestClient) -> None:
    response = client.get("/api/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
