import pytest

from app.llm.client import BaseLLMClient, EmbeddingProfile
from app.schemas.llm import LLMResponse
from app.services.embedding_service import EmbeddingService


class FakeLLMClient(BaseLLMClient):
    @property
    def embedding_profile(self) -> EmbeddingProfile:
        return EmbeddingProfile(
            provider="test",
            model="test-embedding",
            dimension=3,
        )

    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        del messages
        raise NotImplementedError

    async def create_embedding(self, text: str) -> list[float]:
        del text
        return [0.1, 0.2]


@pytest.mark.asyncio
async def test_rejects_embedding_with_unexpected_dimension() -> None:
    service = EmbeddingService(FakeLLMClient())

    with pytest.raises(
        ValueError,
        match="expected 3, got 2",
    ):
        await service.create_embedding("example")
