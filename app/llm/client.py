from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.llm import LLMResponse


@dataclass(frozen=True, slots=True)
class EmbeddingProfile:
    provider: str
    model: str
    dimension: int


class BaseLLMClient(ABC):
    @property
    @abstractmethod
    def embedding_profile(self) -> EmbeddingProfile:
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    async def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        raise NotImplementedError
