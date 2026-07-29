import hashlib
import math

from app.llm.client import BaseLLMClient
from app.schemas.llm import LLMResponse


class MockLLMClient(BaseLLMClient):
    def __init__(self, *, embedding_dimension: int) -> None:
        self.embedding_dimension = embedding_dimension

    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        user_message = next(
            (
                message["content"]
                for message in reversed(messages)
                if message.get("role") == "user"
            ),
            "",
        )

        return LLMResponse(
            text=(
                "Mock provider is active. "
                "No external AI request was made. "
                f'Received message: "{user_message}"'
            ),
            model="mock-llm",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            response_time_ms=0,
        )

    async def create_embedding(self, text: str) -> list[float]:
        digest = hashlib.sha256(
            text.encode("utf-8"),
        ).digest()

        vector = [
            (digest[index % len(digest)] / 127.5) - 1.0
            for index in range(self.embedding_dimension)
        ]

        norm = math.sqrt(
            sum(value * value for value in vector),
        )

        if norm == 0:
            return vector

        return [
            value / norm
            for value in vector
        ]