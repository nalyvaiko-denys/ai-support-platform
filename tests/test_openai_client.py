from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.llm.openai_client import OpenAIClient


def create_test_client(
    monkeypatch: pytest.MonkeyPatch,
    sdk_client: MagicMock,
) -> OpenAIClient:
    def fake_async_openai(
        *,
        api_key: str,
    ) -> MagicMock:
        assert api_key == "test-api-key"
        return sdk_client

    monkeypatch.setattr(
        "app.llm.openai_client.AsyncOpenAI",
        fake_async_openai,
    )

    return OpenAIClient(
        api_key="test-api-key",
        chat_model="gpt-4.1-mini",
        embedding_model="text-embedding-3-small",
        embedding_dimension=3,
    )


@pytest.mark.asyncio
async def test_openai_generate_calls_sdk_correctly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_client = MagicMock()

    sdk_response = SimpleNamespace(
        model="gpt-4.1-mini",
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=("You can change your PIN in the card settings."),
                ),
            ),
        ],
        usage=SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
        ),
    )

    sdk_client.chat.completions.create = AsyncMock(
        return_value=sdk_response,
    )

    client = create_test_client(
        monkeypatch=monkeypatch,
        sdk_client=sdk_client,
    )

    messages = [
        {
            "role": "system",
            "content": ("Answer only using the knowledge-base context."),
        },
        {
            "role": "user",
            "content": "How can I change my card PIN?",
        },
    ]

    result = await client.generate(messages)

    sdk_client.chat.completions.create.assert_awaited_once_with(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.2,
    )

    assert result.text == ("You can change your PIN in the card settings.")
    assert result.model == "gpt-4.1-mini"
    assert result.prompt_tokens == 100
    assert result.completion_tokens == 20
    assert result.total_tokens == 120
    assert result.response_time_ms >= 0


@pytest.mark.asyncio
async def test_openai_embedding_calls_sdk_correctly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_client = MagicMock()

    expected_embedding = [
        0.1,
        0.2,
        0.3,
    ]

    sdk_client.embeddings.create = AsyncMock(
        return_value=SimpleNamespace(
            data=[
                SimpleNamespace(
                    embedding=expected_embedding,
                ),
            ],
        ),
    )

    client = create_test_client(
        monkeypatch=monkeypatch,
        sdk_client=sdk_client,
    )

    result = await client.create_embedding("How can I change my card PIN?")

    sdk_client.embeddings.create.assert_awaited_once_with(
        input="How can I change my card PIN?",
        model="text-embedding-3-small",
        dimensions=3,
    )

    assert result == expected_embedding
