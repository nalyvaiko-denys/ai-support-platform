from abc import ABC, abstractmethod
from typing import Any

from app.schemas.llm import LLMResponse


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def create_embedding(self, text: str) -> list[float]:
        raise NotImplementedError