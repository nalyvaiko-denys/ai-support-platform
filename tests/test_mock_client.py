import math

import pytest

from app.llm.mock_client import MockLLMClient


@pytest.mark.asyncio
async def test_mock_client_returns_expected_response() -> None:
    client = MockLLMClient(
        embedding_dimension=1536,
    )

    response = await client.generate(
        [
            {
                "role": "system",
                "content": "System instructions",
            },
            {
                "role": "user",
                "content": "How can I change my card PIN?",
            },
        ]
    )

    assert response.text == (
        "Mock provider is active. "
        "No external AI request was made. "
        'Received message: "How can I change my card PIN?"'
    )
    assert response.model == "mock-llm"
    assert response.prompt_tokens == 0
    assert response.completion_tokens == 0
    assert response.total_tokens == 0
    assert response.response_time_ms == 0


@pytest.mark.asyncio
async def test_mock_embedding_is_deterministic() -> None:
    client = MockLLMClient(
        embedding_dimension=1536,
    )

    first = await client.create_embedding(
        "How can I change my card PIN?"
    )
    second = await client.create_embedding(
        "How can I change my card PIN?"
    )

    assert first == second
    assert len(first) == 1536


@pytest.mark.asyncio
async def test_mock_embedding_is_normalized() -> None:
    client = MockLLMClient(
        embedding_dimension=1536,
    )

    embedding = await client.create_embedding(
        "How can I change my card PIN?"
    )

    vector_length = math.sqrt(
        sum(value * value for value in embedding),
    )

    assert math.isclose(
        vector_length,
        1.0,
        rel_tol=1e-9,
    )