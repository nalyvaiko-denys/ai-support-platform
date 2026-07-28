import math

import pytest

from app.llm.mock_client import MockLLMClient


@pytest.mark.asyncio
async def test_generates_deterministic_demo_response() -> None:
    client = MockLLMClient(
        embedding_dimension=32,
    )

    response = await client.generate(
        [
            {
                "role": "user",
                "content": "Як змінити PIN-код?",
            },
        ]
    )

    assert response.model == "mock-llm"
    assert "Як змінити PIN-код?" in response.text
    assert response.total_tokens == 0
    assert response.response_time_ms == 0


@pytest.mark.asyncio
async def test_creates_deterministic_normalized_embedding() -> None:
    client = MockLLMClient(
        embedding_dimension=32,
    )

    first = await client.create_embedding(
        "same text"
    )
    second = await client.create_embedding(
        "same text"
    )
    different = await client.create_embedding(
        "different text"
    )

    assert len(first) == 32
    assert first == second
    assert first != different

    norm = math.sqrt(
        sum(
            value * value
            for value in first
        )
    )

    assert math.isclose(
        norm,
        1.0,
        rel_tol=1e-9,
    )
